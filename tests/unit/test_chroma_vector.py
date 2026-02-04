"""
Unit tests for ChromaDB Vector Database Interface.

Tests functionality of ChromaVectorDB including embedding generation,
document storage, semantic search, and error handling.
"""

import pytest
import shutil
from pathlib import Path

from mind_q_agent.vector.chroma_vector import ChromaVectorDB


class TestChromaVectorDB:
    """Test suite for ChromaVectorDB class."""
    
    @pytest.fixture
    def vector_db(self, tmp_path):
        """
        Create a temporary vector database for testing.
        
        Args:
            tmp_path: pytest tmp_path fixture
            
        Yields:
            ChromaVectorDB instance
        """
        # Use a very small model for faster testing
        # paraphrase-albert-small-v2 is fast but still good for testing
        # or we can use the default but it might slow down tests slightly
        db_path = tmp_path / "test_vector_db"
        db = ChromaVectorDB(str(db_path), model_name="all-MiniLM-L6-v2")
        yield db
        
        # Cleanup is handled by tmp_path, but explicitly deleting collection is good practice
        try:
            db.delete_collection()
        except:
            pass
    
    def test_initialization(self, tmp_path):
        """Test database initialization."""
        db_path = tmp_path / "init_test_db"
        db = ChromaVectorDB(str(db_path))
        
        # Verify connection
        assert db.client is not None
        assert db.collection is not None
        assert db.model is not None
        assert db.collection.name == "mind_q_docs"

    def test_add_documents_valid(self, vector_db):
        """Test adding documents correctly."""
        docs = ["Hello world", "Machine learning is cool"]
        metadatas = [{"source": "test1"}, {"source": "test2"}]
        ids = ["doc1", "doc2"]
        
        vector_db.add_documents(docs, metadatas, ids)
        
        assert vector_db.count() == 2

    def test_add_documents_mismatched_lengths(self, vector_db):
        """Test that mismatched input lists raise ValueError."""
        docs = ["Doc1"]
        metadatas = [{"source": "test1"}, {"source": "test2"}] # 2 items
        ids = ["doc1"]
        
        with pytest.raises(ValueError, match="must have the same length"):
            vector_db.add_documents(docs, metadatas, ids)

    def test_query_similar(self, vector_db):
        """Test semantic search functionality."""
        # Add related documents
        docs = [
            "Apple is a fruit",
            "Banana is yellow",
            "Python is a programming language",
            "Java is also a language"
        ]
        metadatas = [{"type": "fruit"}, {"type": "fruit"}, {"type": "tech"}, {"type": "tech"}]
        ids = ["1", "2", "3", "4"]
        
        vector_db.add_documents(docs, metadatas, ids)
        
        # Query for fruit
        results = vector_db.query_similar("green apple", n_results=2)
        
        assert len(results) == 2
        # First result should likely be apple or banana (fruits)
        # Note: distance is smaller for closer matches
        assert results[0]['metadata']['type'] == "fruit"
        
        # Check structure
        assert 'id' in results[0]
        assert 'document' in results[0]
        assert 'metadata' in results[0]
        assert 'distance' in results[0]

    def test_query_with_filter(self, vector_db):
        """Test querying with metadata filters."""
        docs = ["Content A", "Content B", "Content C"]
        metadatas = [{"tag": "alpha"}, {"tag": "beta"}, {"tag": "alpha"}]
        ids = ["1", "2", "3"]
        
        vector_db.add_documents(docs, metadatas, ids)
        
        # Query only 'beta' tag
        results = vector_db.query_similar("Content", n_results=5, where={"tag": "beta"})
        
        assert len(results) == 1
        assert results[0]['id'] == "2"

    def test_count(self, vector_db):
        """Test counting documents."""
        assert vector_db.count() == 0
        
        vector_db.add_documents(["test"], [{"a": 1}], ["id1"])
        assert vector_db.count() == 1
        
        vector_db.add_documents(["test2"], [{"a": 2}], ["id2"])
        assert vector_db.count() == 2

    def test_delete_collection(self, vector_db):
        """Test deleting the collection."""
        vector_db.add_documents(["test"], [{"status": "test"}], ["id1"])
        assert vector_db.count() == 1
        
        vector_db.delete_collection()
        
        # Client should throw error if we try to access deleted collection via old reference
        # or we might need to recreate it to verify it's empty.
        # Checking logic mostly relies on no error raised during delete.
        
        # Re-get collection to verify it's empty/new
        new_collection = vector_db.client.get_or_create_collection("mind_q_docs")
        assert new_collection.count() == 0

    def test_add_empty_documents(self, vector_db):
        """Test adding empty lists does nothing."""
        initial_count = vector_db.count()
        vector_db.add_documents([], [], [])
        assert vector_db.count() == initial_count

