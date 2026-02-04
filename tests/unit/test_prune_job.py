import pytest
from unittest.mock import MagicMock, patch
from mind_q_agent.learning.prune_job import PruneJob

class TestPruneJob:
    """Unit tests for PruneJob."""

    @pytest.fixture
    def mock_graph_db(self):
        return MagicMock()

    @pytest.fixture
    def job(self, mock_graph_db):
        return PruneJob(mock_graph_db)

    @patch('mind_q_agent.learning.prune_job.get_edges_to_prune')
    @patch('mind_q_agent.learning.prune_job.prune_edges')
    def test_run_prunes_edges(self, mock_prune, mock_get, job):
        """Should get and prune edges."""
        mock_get.return_value = [1, 2, 3]
        mock_prune.return_value = 3
        
        count = job.run()
        
        assert count == 3
        mock_get.assert_called_once()
        mock_prune.assert_called_once_with(job.graph_db, [1, 2, 3])

    @patch('mind_q_agent.learning.prune_job.get_edges_to_prune')
    @patch('mind_q_agent.learning.prune_job.prune_edges')
    def test_run_no_edges(self, mock_prune, mock_get, job):
        """Should return 0 if no edges to prune."""
        mock_get.return_value = []
        
        count = job.run()
        
        assert count == 0
        mock_prune.assert_not_called()

    @patch('mind_q_agent.learning.prune_job.get_edges_to_prune')
    def test_run_with_custom_threshold(self, mock_get, job):
        """Should pass threshold to get_edges_to_prune."""
        mock_get.return_value = []
        
        job.run(threshold=0.2)
        
        mock_get.assert_called_once_with(job.graph_db, threshold=0.2)
