import queue
import threading
import time
from unittest.mock import MagicMock, ANY

import pytest
from mind_q_agent.ingestion.worker import IngestionWorker
from mind_q_agent.ingestion.pipeline import IngestionPipeline

class TestIngestionWorker:
    """Unit tests for IngestionWorker thread."""
    
    @pytest.fixture
    def mock_pipeline(self):
        return MagicMock(spec=IngestionPipeline)
        
    @pytest.fixture
    def event_queue(self):
        return queue.Queue()
        
    @pytest.fixture
    def worker(self, event_queue, mock_pipeline):
        worker = IngestionWorker(event_queue, mock_pipeline)
        return worker

    def test_process_item(self, worker, event_queue, mock_pipeline):
        """Test processing a valid item."""
        event = {
            "filepath": "/tmp/test.txt",
            "text": "Hello",
            "filename": "test.txt"
        }
        
        # Start worker
        worker.start()
        
        # Put item
        event_queue.put(event)
        
        # Put stop signal to ensure thread ends
        event_queue.put("STOP")
        
        # Wait for join with timeout
        worker.join(timeout=2.0)
        
        assert not worker.is_alive()
        
        # Verify pipeline called
        mock_pipeline.process_document.assert_called_once()
        args, _ = mock_pipeline.process_document.call_args
        assert str(args[0]) == "/tmp/test.txt"
        assert args[1] == "Hello"

    def test_stop_signal(self, worker, event_queue, mock_pipeline):
        """Test stopping via Sentinel."""
        worker.start()
        event_queue.put("STOP")
        worker.join(timeout=1.0)
        assert not worker.is_alive()
        mock_pipeline.process_document.assert_not_called()

    def test_exception_resilience(self, worker, event_queue, mock_pipeline):
        """Test worker survives pipeline exceptions."""
        # 1. First item: causes error
        mock_pipeline.process_document.side_effect = RuntimeError("Pipeline Boom")
        
        event1 = {"filepath": "/tmp/bad.txt", "text": "bad", "filename": "bad.txt"}
        event2 = {"filepath": "/tmp/good.txt", "text": "good", "filename": "good.txt"}
        
        worker.start()
        
        event_queue.put(event1)
        event_queue.put(event2)
        event_queue.put("STOP")
        
        worker.join(timeout=2.0)
        
        assert not worker.is_alive()
        
        # Verify both attempts made
        assert mock_pipeline.process_document.call_count == 2
        
        # Verify queue Empty
        assert event_queue.empty()

    def test_invalid_item(self, worker, event_queue, mock_pipeline):
        """Test handling invalid queue items."""
        worker.start()
        
        event_queue.put("INVALID_STRING_NOT_DICT")
        event_queue.put("STOP")
        
        worker.join(timeout=1.0)
        
        # Pipeline should NOT be called for invalid item
        mock_pipeline.process_document.assert_not_called()
