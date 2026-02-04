import hashlib
import logging
from pathlib import Path
from typing import List, Optional

from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.vector.chroma_vector import ChromaVectorDB
from mind_q_agent.extraction.entity_extractor import EntityExtractor

logger = logging.getLogger(__name__)

class IngestionPipeline:
    """
    Core pipeline for ingesting documents into the Mind-Q knowledge system.
    Orchestrates flow between Raw Text -> Extractor -> Vector DB -> Graph DB.
    """
    
    def __init__(self, graph_db: KuzuGraphDB, vector_store: ChromaVectorDB):
        self.graph_db = graph_db
        self.vector_store = vector_store
        self.extractor = EntityExtractor()

    def process_document(self, file_path: Path, text: str) -> bool:
        """
        Process a single document.
        
        Args:
            file_path: Absolute path to the file
            text: Raw text content
            
        Returns:
            True if successfully processed, False otherwise (e.g. duplicate)
        """
        try:
            # 1. Generate file hash (SHA256)
            file_hash = self._calculate_hash(text)
            
            # 2. Check Graph for existing Document node (deduplication)
            if self._document_exists(file_hash):
                logger.info(f"Skipping duplicate document: {file_path.name}")
                return False
                
            logger.info(f"Processing new document: {file_path.name}")
            
            # 3. Extract entities/concepts
            extracted_data = self.extractor.extract_all(text)
            
            # Combine entities and concepts for graph nodes
            # Entities have label info, concepts are just strings.
            # For this Phase, we treat them similarly but could use labels for categories.
            
            # 4. Store in VectorDB
            self.vector_store.add_documents(
                documents=[text],
                metadatas=[{
                    "source": str(file_path),
                    "filename": file_path.name
                }],
                ids=[file_hash]
            )
            
            # 5. Store in GraphDB
            # Create Document Node
            self._create_document_node(file_path, file_hash, len(text))
            
            # Create Concept Nodes and Edges
            # Process generic concepts
            for concept in extracted_data["concepts"]:
                self._process_concept(file_hash, concept, "General")
                
            # Process named entities
            for entity in extracted_data["entities"]:
                # entity is dict {'text': '...', 'label': '...'}
                self._process_concept(file_hash, entity['text'], entity['label'])

            # 6. Create Co-occurrence Edges (Concept <-> Concept)
            all_concept_names = extracted_data["concepts"] + [e['text'] for e in extracted_data["entities"]]
            self._create_concept_edges(all_concept_names)

            logger.info(f"Successfully processed {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            raise e

    def _process_concept(self, doc_hash: str, name: str, category: str):
        """Helper to create concept node and link to document."""
        try:
            # Generate embedding for the concept/entity name
            embedding = self.vector_store.get_embedding(name)
            
            self.graph_db.create_concept(
                name=name,
                embedding=embedding,
                category=category
            )
        except Exception:
            # Ignore if exists
            pass
            
        self._create_discusses_edge(doc_hash, name)

    def _calculate_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _document_exists(self, file_hash: str) -> bool:
        """Check if document already exists in Graph."""
        query = "MATCH (d:Document {hash: $hash}) RETURN d"
        df = self.graph_db.execute(query, {'hash': file_hash})
        return not df.empty

    def _create_document_node(self, path: Path, file_hash: str, size: int):
        """Create the Document node in KuzuDB."""
        from datetime import datetime
        query = """
            CREATE (d:Document {
                hash: $hash,
                title: $filename,
                source_path: $path,
                source_type: $ext,
                created_at: $created_at,
                size_bytes: $size
            })
        """
        params = {
            'hash': file_hash,
            'filename': path.name,
            'path': str(path),
            'ext': path.suffix,
            'created_at': datetime.now().isoformat(),
            'size': size
        }
        self.graph_db.execute(query, params)

    def _create_discusses_edge(self, doc_hash: str, concept_name: str):
        """Create DISCUSSES edge between Document and Concept."""
        query = """
            MATCH (d:Document {hash: $doc_hash}), (c:Concept {name: $concept})
            CREATE (d)-[:DISCUSSES {strength: 1.0}]->(c)
        """
        self.graph_db.execute(query, {'doc_hash': doc_hash, 'concept': concept_name})
    def _create_concept_edges(self, concepts: List[str]):
        """
        Create RELATED_TO edges between all co-occurring concepts.
        This forms the semantic network foundation.
        """
        if len(concepts) < 2:
            return

        import itertools
        
        # Deduplicate and sort for consistent edge creation
        unique_concepts = sorted(list(set(concepts)))
        
        for c1, c2 in itertools.combinations(unique_concepts, 2):
            # Create undirected edge (conceptually). 
            # In GraphDB we often create one directed edge or two if strictly directed.
            # Kuzu's RELATED_TO is likely directed in schema, but semantically symmetric here.
            # We'll create one direction for minimal redundancy, or based on lexicographical order.
            
            from datetime import datetime
            query = """
                MATCH (a:Concept {name: $c1}), (b:Concept {name: $c2})
                OPTIONAL MATCH (a)-[r:RELATED_TO]->(b)
                WITH a, b, r
                WHERE r IS NULL
                CREATE (a)-[:RELATED_TO {
                    base_weight: 1.0, 
                    current_weight: 1.0,
                    sample_size: 1,
                    confidence: 0.5,
                    observation_variance: 0.0,
                    last_accessed: $now_ts,
                    decay_rate: 0.01
                }]->(b)
            """
            
            # Use 'create if not exists' logic logic via MERGE if Kuzu fully supports it,
            # but here explicit check via OPTIONAL MATCH is safer for Kuzu versions.
            # Or just blindly CREATE if we accept potential dupes (cleaner is better).
            # Let's use the query above.
            
            try:
                self.graph_db.execute(query, {'c1': c1, 'c2': c2, 'now_ts': datetime.now().isoformat()})
            except Exception as e:
                logger.warning(f"Failed to link concepts {c1}-{c2}: {e}")
