import pytest
from unittest.mock import MagicMock
from mind_q_agent.learning.pruning import get_edges_to_prune, prune_edges

class TestPruning:
    """Unit tests for graph pruning functions."""

    @pytest.fixture
    def mock_graph_db(self):
        return MagicMock()

    def test_get_edges_to_prune_returns_ids(self, mock_graph_db):
        """Should return edge IDs below threshold."""
        mock_graph_db.execute.return_value = [(1,), (2,), (3,)]
        
        ids = get_edges_to_prune(mock_graph_db, threshold=0.1)
        
        assert ids == [1, 2, 3]
        mock_graph_db.execute.assert_called_once()

    def test_get_edges_to_prune_empty(self, mock_graph_db):
        """Should return empty list if no edges below threshold."""
        mock_graph_db.execute.return_value = []
        
        ids = get_edges_to_prune(mock_graph_db, threshold=0.1)
        
        assert ids == []

    def test_prune_edges_deletes(self, mock_graph_db):
        """Should delete each edge by ID."""
        mock_graph_db.execute.return_value = None
        
        count = prune_edges(mock_graph_db, [1, 2, 3])
        
        assert count == 3
        assert mock_graph_db.execute.call_count == 3

    def test_prune_edges_empty_list(self, mock_graph_db):
        """Should return 0 if no edges to prune."""
        count = prune_edges(mock_graph_db, [])
        
        assert count == 0
        mock_graph_db.execute.assert_not_called()

    def test_prune_edges_handles_error(self, mock_graph_db):
        """Should continue even if one deletion fails."""
        mock_graph_db.execute.side_effect = [None, Exception("DB Error"), None]
        
        count = prune_edges(mock_graph_db, [1, 2, 3])
        
        assert count == 2  # 2 succeeded, 1 failed
