import logging
import pytest
from unittest.mock import MagicMock, ANY
from pathlib import Path
from mind_q_agent.ingestion.pipeline import IngestionPipeline
from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.vector.chroma_vector import ChromaVectorDB

from mind_q_agent.extraction.entity_extractor import EntityExtractor

class TestIngestionPipeline:
    """Unit tests for the Ingestion Pipeline logic."""
    
    @pytest.fixture
    def mock_graph_db(self):
        return MagicMock(spec=KuzuGraphDB)

    @pytest.fixture
    def mock_vector_store(self):
        return MagicMock(spec=ChromaVectorDB)

    @pytest.fixture
    def mock_extractor(self):
        return MagicMock(spec=EntityExtractor)

    @pytest.fixture
    def pipeline(self, mock_graph_db, mock_vector_store, mock_extractor):
        # We need to patch the internal extractor creation OR inject it.
        # But the __init__ creates it: self.extractor = EntityExtractor()
        # So we should patch the class instantiation or set the attribute after init.
        # Let's use patch in the context of the test, or just set the attribute.
        pipe = IngestionPipeline(mock_graph_db, mock_vector_store)
        pipe.extractor = mock_extractor
        return pipe

    def test_calculate_hash(self, pipeline):
        """Test SHA-256 hash generation."""
        text = "Hello World"
        # Known hash for "Hello World"
        expected_hash = "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"
        assert pipeline._calculate_hash(text) == expected_hash

    def test_process_duplicate_document(self, pipeline, mock_graph_db):
        """Test that duplicate documents are skipped."""
        # Setup duplicate check to return a non-empty result (simulating existence)
        mock_graph_db.execute.return_value.empty = False 
        
        path = Path("/tmp/test.txt")
        text = "Duplicate content"
        
        result = pipeline.process_document(path, text)
        
        assert result is False
        mock_graph_db.execute.assert_called_once() # Checked existence
        pipeline.vector_store.add_documents.assert_not_called() # Skipped storage

    def test_process_new_document(self, pipeline, mock_graph_db, mock_vector_store, mock_extractor):
        """Test full flow for a new document."""
        # 1. Setup duplicate check to return empty (simulating NEW doc)
        mock_result = MagicMock()
        mock_result.empty = True
        mock_graph_db.execute.return_value = mock_result
        
        # 2. Setup Vector Store embedding return
        mock_vector_store.get_embedding.return_value = [0.1] * 384
        
        # 3. Setup Extractor return
        mock_extractor.extract_all.return_value = {
            "entities": [{"text": "Musk", "label": "PERSON"}],
            "dates": [],
            "emails": [],
            "concepts": ["space"]
        }
        
        path = Path("/tmp/new_doc.txt")
        text = "Musk likes space."
        
        result = pipeline.process_document(path, text)
        
        assert result is True
        
        # Verify Duplicate Check
        args, _ = mock_graph_db.execute.call_args_list[0]
        assert "MATCH (d:Document" in args[0]
        
        # Verify Vector Storage
        mock_vector_store.add_documents.assert_called_once()
        
        # Verify Graph Storage
        # Expected: Document + Concept(space, General) + Concept(Musk, PERSON)
        
    def test_cooccurrence_edges(self, pipeline, mock_graph_db, mock_vector_store, mock_extractor):
        """Test creation of RELATED_TO edges between co-occurring concepts."""
        # Setup clean path through process_document
        mock_graph_db.execute.return_value.empty = True # New doc
        mock_vector_store.get_embedding.return_value = [0.0] * 384
        
        # Setup Extractor to return multiple items
        mock_extractor.extract_all.return_value = {
            "entities": [{"text": "Alice", "label": "PERSON"}, {"text": "Tesla", "label": "ORG"}],
            "dates": [],
            "emails": [],
            "concepts": ["Innovation"]
        }
        
        pipeline.process_document(Path("/tmp/test.txt"), "Alice works at Tesla on Innovation.")
        
        # We expect edges between:
        # (Alice, Tesla), (Alice, Innovation), (Innovation, Tesla)
        # Total 3 pairs (unique).
        
        # Get all execute calls
        execute_calls = mock_graph_db.execute.call_args_list
        query_strings = [call.args[0] for call in execute_calls]
        
        # Filter for RELATED_TO queries
        edge_queries = [q for q in query_strings if "RELATED_TO" in q]
        
        assert len(edge_queries) == 3
        
        # Check specific combinations were attempted (order sorted alphabetically in implementation)
        # Concepts: Alice, Innovation, Tesla
        # Pairs: (Alice, Innovation), (Alice, Tesla), (Innovation, Tesla)
        
        # Verify one call args for correctness
        found_alice_tesla = False
        for call in execute_calls:
            params = call.args[1] if len(call.args) > 1 else {}
            if params.get('c1') == 'Alice' and params.get('c2') == 'Tesla':
                found_alice_tesla = True
                break
        
        assert found_alice_tesla, "Edge between Alice and Tesla not found"
