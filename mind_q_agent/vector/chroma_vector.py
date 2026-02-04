"""
ChromaDB Vector Database Interface for Mind-Q Agent.

This module provides a production-ready interface to ChromaDB for managing
document embeddings and semantic search functionality.
"""

import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class ChromaVectorDB:
    """
    ChromaDB Vector Database Interface.
    
    Manages vector embeddings for documents and concepts using ChromaDB
    and SentenceTransformers for embedding generation.
    
    Attributes:
        db_path: Path to the database directory
        client: ChromaDB client instance
        collection: ChromaDB collection for documents
        model: SentenceTransformer model for embedding generation
    """
    
    def __init__(
        self, 
        db_path: str, 
        collection_name: str = "mind_q_docs",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize ChromaDB connection and embedding model.
        
        Args:
            db_path: Path to the database directory
            collection_name: Name of the collection to use
            model_name: Name of the SentenceTransformer model
            
        Raises:
            RuntimeError: If initialization fails
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=str(self.db_path))
            
            # Initialize embedding model
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"Connected to ChromaDB at {self.db_path}, collection: {collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise RuntimeError(f"Vector DB initialization failed: {e}") from e

    def add_documents(
        self, 
        documents: List[str], 
        metadatas: List[Dict[str, Any]], 
        ids: List[str]
    ) -> None:
        """
        Add documents to the vector database.
        
        Generates embeddings automatically using the initialized model.
        
        Args:
            documents: List of text content
            metadatas: List of metadata dictionaries
            ids: List of unique document IDs
            
        Raises:
            ValueError: If input lists have different lengths
            RuntimeError: If adding documents fails
        """
        if not (len(documents) == len(metadatas) == len(ids)):
            raise ValueError("documents, metadatas, and ids must have the same length")
        
        if not documents:
            return

        try:
            # Generate embeddings
            embeddings = self.model.encode(documents).tolist()
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise RuntimeError(f"Failed to add documents: {e}") from e

    def query_similar(
        self, 
        query: str, 
        n_results: int = 5, 
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic search.
        
        Args:
            query: Query text
            n_results: Number of results to return
            where: Optional metadata filter
            
        Returns:
            List of results with metadata, distance, and document content.
            Format: [{'id': id, 'document': text, 'metadata': dict, 'distance': float}, ...]
        """
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query]).tolist()
            
            # Execute query
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=where
            )
            
            # Parse results into a friendly format
            parsed_results = []
            if results['ids']:
                # ChromaDB returns lists of lists (one list per query)
                count = len(results['ids'][0])
                for i in range(count):
                    parsed_results.append({
                        'id': results['ids'][0][i],
                        'document': results['documents'][0][i] if results['documents'] else "",
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []

    def count(self) -> int:
        """
        Get the total number of documents in the collection.
        
        Returns:
            Document count
        """
        return self.collection.count()

    def delete_collection(self) -> None:
        """
        Delete the collection. Useful for cleanup or testing.
        """
        try:
            self.client.delete_collection(self.collection.name)
            logger.info(f"Deleted collection: {self.collection.name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise RuntimeError(f"Failed to delete collection: {e}") from e
