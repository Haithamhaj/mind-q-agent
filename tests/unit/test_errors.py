import logging
import pytest
from unittest.mock import MagicMock
from mind_q_agent.utils.errors import (
    MindQError, DatabaseError, IngestionError, ExtractionError, log_error
)

class TestErrorHandling:
    """Tests for custom error classes and logging utility."""
    
    def test_base_exception(self):
        """Test MindQError base class."""
        err = MindQError("Something wrong")
        assert str(err) == "Something wrong"
        assert err.message == "Something wrong"
        assert err.original_exception is None
        
    def test_chained_exception(self):
        """Test chaining original exceptions."""
        orig = ValueError("bad value")
        err = DatabaseError("DB failed", original_exception=orig)
        assert err.original_exception == orig
        assert isinstance(err, MindQError)
        
    def test_subclasses(self):
        """Test all subclasses inherit correctly."""
        assert issubclass(DatabaseError, MindQError)
        assert issubclass(IngestionError, MindQError)
        assert issubclass(ExtractionError, MindQError)
        
    def test_log_error_custom(self):
        """Test logging a custom MindQError."""
        mock_logger = MagicMock(spec=logging.Logger)
        err = IngestionError("File bad")
        
        log_error(mock_logger, err, context="Ingest")
        
        mock_logger.error.assert_called_once_with("Ingest: File bad")
        
    def test_log_error_chained(self):
        """Test logging a chained error."""
        mock_logger = MagicMock(spec=logging.Logger)
        orig = KeyError("missing")
        err = ExtractionError("Extract failed", original_exception=orig)
        
        log_error(mock_logger, err)
        
        # Should include both messages
        args = mock_logger.error.call_args[0][0]
        assert "Extract failed" in args
        assert "Caused by: 'missing'" in args
        
    def test_log_error_unexpected(self):
        """Test logging a standard non-MindQ exception."""
        mock_logger = MagicMock(spec=logging.Logger)
        err = RuntimeError("Crash")
        
        log_error(mock_logger, err, context="Main")
        
        # Should call exception() for stack trace
        mock_logger.exception.assert_called_once()
        args = mock_logger.exception.call_args[0][0]
        assert "Main: Unexpected error: Crash" in args
