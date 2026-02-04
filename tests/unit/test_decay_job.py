import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from mind_q_agent.learning.decay_job import DecayJob

class TestDecayJob:
    """Unit tests for DecayJob."""

    @pytest.fixture
    def mock_graph_db(self):
        return MagicMock()

    @pytest.fixture
    def custom_config(self):
        return {"decay_rate": 0.1}

    @pytest.fixture
    def job(self, mock_graph_db, custom_config):
        return DecayJob(mock_graph_db, config=custom_config)

    def test_run_no_edges(self, job, mock_graph_db):
        """No edges to process."""
        mock_graph_db.execute.return_value = []
        
        count = job.run()
        
        assert count == 0

    def test_run_decays_old_edges(self, job, mock_graph_db):
        """Edges older than 1 day should be decayed."""
        # Simulate an edge with last_updated 7 days ago
        old_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        
        # First call returns edges, subsequent calls are updates
        mock_graph_db.execute.side_effect = [
            [(1, 0.8, old_date)],  # Query result
            None,  # Update result
        ]
        
        count = job.run()
        
        assert count == 1
        # Verify update was called
        assert mock_graph_db.execute.call_count == 2

    def test_run_skips_recent_edges(self, job, mock_graph_db):
        """Edges updated less than 1 day ago should be skipped."""
        recent_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        mock_graph_db.execute.return_value = [(1, 0.8, recent_date)]
        
        count = job.run()
        
        assert count == 0
        # Only the query call, no update
        assert mock_graph_db.execute.call_count == 1

    def test_run_handles_null_weight(self, job, mock_graph_db):
        """Edges with NULL weight should use default 0.5."""
        old_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
        
        mock_graph_db.execute.side_effect = [
            [(1, None, old_date)],  # NULL weight
            None,
        ]
        
        count = job.run()
        
        assert count == 1
