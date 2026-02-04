import pytest
from unittest.mock import MagicMock, patch
from mind_q_agent.learning.updater import HebbianUpdater

class TestHebbianUpdater:
    """Unit tests for HebbianUpdater."""

    @pytest.fixture
    def mock_tracker(self):
        tracker = MagicMock()
        return tracker

    @pytest.fixture
    def mock_graph_db(self):
        graph_db = MagicMock()
        return graph_db

    @pytest.fixture
    def custom_config(self):
        return {
            "alpha": 0.2,
            "event_scores": {
                "CLICK": 1.0,
                "SEARCH": 0.5,
                "VIEW_BASE": 0.3,
                "VIEW_MAX": 1.0
            }
        }

    @pytest.fixture
    def updater(self, mock_tracker, mock_graph_db, custom_config):
        return HebbianUpdater(mock_tracker, mock_graph_db, config=custom_config)

    def test_run_update_cycle_no_interactions(self, updater, mock_tracker):
        """If no unprocessed interactions, return 0."""
        mock_tracker.get_unprocessed_interactions.return_value = []
        
        result = updater.run_update_cycle()
        
        assert result == 0
        mock_tracker.mark_as_processed.assert_not_called()

    def test_run_update_cycle_processes_interactions(self, updater, mock_tracker, mock_graph_db):
        """Verify interactions are processed and edges updated."""
        # Setup mock data
        mock_tracker.get_unprocessed_interactions.return_value = [
            {"id": 1, "event_type": "CLICK", "target_id": "concept_A", "duration_sec": None},
            {"id": 2, "event_type": "VIEW", "target_id": "concept_A", "duration_sec": 10.0},
        ]
        
        # Mock graph query result (edge found)
        mock_graph_db.execute.return_value = [
            (123, 0.5)  # edge_id, current_weight
        ]
        
        result = updater.run_update_cycle()
        
        # Should process 2 interactions
        assert result == 2
        mock_tracker.mark_as_processed.assert_called_once_with([1, 2])
        
        # Verify edge update query was called
        assert mock_graph_db.execute.call_count >= 2 # 1 for query, 1 for update

    def test_run_update_cycle_handles_missing_target_id(self, updater, mock_tracker):
        """Events without target_id should be skipped but still processed."""
        mock_tracker.get_unprocessed_interactions.return_value = [
            {"id": 1, "event_type": "SEARCH", "target_id": None, "query": "test"},
        ]
        
        result = updater.run_update_cycle()
        
        # Empty grouped dict means no edge updates, but tracker should still be called
        assert result == 0
