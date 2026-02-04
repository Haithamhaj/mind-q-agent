import pytest
from unittest.mock import MagicMock
from mind_q_agent.learning.scheduler import MaintenanceScheduler

class TestMaintenanceScheduler:
    """Unit tests for MaintenanceScheduler."""

    @pytest.fixture
    def scheduler(self):
        return MaintenanceScheduler()

    def test_add_job(self, scheduler):
        """Should register a job."""
        mock_fn = MagicMock(return_value=5)
        
        scheduler.add_job("test_job", mock_fn, interval_hours=1.0)
        
        assert len(scheduler._jobs) == 1
        assert scheduler._jobs[0]["name"] == "test_job"

    def test_run_all_now(self, scheduler):
        """Should run all registered jobs."""
        mock_fn1 = MagicMock(return_value=3)
        mock_fn2 = MagicMock(return_value=5)
        
        scheduler.add_job("job1", mock_fn1, interval_hours=1.0)
        scheduler.add_job("job2", mock_fn2, interval_hours=2.0)
        
        results = scheduler.run_all_now()
        
        assert results["job1"] == 3
        assert results["job2"] == 5
        mock_fn1.assert_called_once()
        mock_fn2.assert_called_once()

    def test_run_all_now_handles_error(self, scheduler):
        """Should continue if one job fails."""
        mock_fn1 = MagicMock(side_effect=Exception("Boom"))
        mock_fn2 = MagicMock(return_value=5)
        
        scheduler.add_job("job1", mock_fn1, interval_hours=1.0)
        scheduler.add_job("job2", mock_fn2, interval_hours=2.0)
        
        results = scheduler.run_all_now()
        
        assert results["job1"] == -1  # Error indicator
        assert results["job2"] == 5

    def test_start_stop(self, scheduler):
        """Should start and stop without error."""
        scheduler.start()
        assert scheduler._running is True
        
        scheduler.stop()
        assert scheduler._running is False
