import pytest
from unittest.mock import MagicMock
from mind_q_agent.search.engine import SearchEngine
from mind_q_agent.vector.chroma_vector import ChromaVectorDB

class TestSearchEngine:
    """Unit tests for the Search Engine."""

    @pytest.fixture
    def mock_vector_store(self):
        return MagicMock(spec=ChromaVectorDB)

    @pytest.fixture
    def search_engine(self, mock_vector_store):
        return SearchEngine(mock_vector_store)

    def test_search_valid_query(self, search_engine, mock_vector_store):
        """Test searching with a valid query."""
        # Setup mock return
        mock_vector_store.query_similar.return_value = [
            {
                "id": "hash123",
                "document": "This is a relevant document.",
                "distance": 0.25,
                "metadata": {"source": "doc1.txt"}
            }
        ]
        
        results = search_engine.search("relevant doc", limit=3)
        
        # Verify vector store call
        mock_vector_store.query_similar.assert_called_once_with("relevant doc", n_results=3)
        
        # Verify result format
        assert len(results) == 1
        res = results[0]
        assert res["id"] == "hash123"
        assert res["text"] == "This is a relevant document."
        assert res["score"] == 0.25
        assert res["metadata"]["source"] == "doc1.txt"

    def test_search_empty_query(self, search_engine, mock_vector_store):
        """Test that empty queries return empty list immediately."""
        results = search_engine.search("   ")
        assert results == []
        mock_vector_store.query_similar.assert_not_called()

    def test_search_error_handling(self, search_engine, mock_vector_store):
        """Test resilience against vector store errors."""
        mock_vector_store.query_similar.side_effect = RuntimeError("DB Connection Failed")
        
        results = search_engine.search("crash me")
        
        # Should return empty list and log error (not raise)
        assert results == []
        mock_vector_store.query_similar.assert_called_once()
