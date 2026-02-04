from typing import Optional
import logging

class MindQError(Exception):
    """Base exception class for Mind-Q Agent."""
    
    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception

class DatabaseError(MindQError):
    """Raised when a database operation fails."""
    pass

class IngestionError(MindQError):
    """Raised when file ingestion fails."""
    pass

class ExtractionError(MindQError):
    """Raised when entity extraction fails."""
    pass

def log_error(logger: logging.Logger, error: Exception, context: str = "") -> None:
    """
    Utility to format and log standard exceptions.
    
    Args:
        logger: Logger instance to use
        error: The exception caught
        context: Optional context string (e.g. "Processing file X")
    """
    if isinstance(error, MindQError):
        msg = f"{context}: {error.message}" if context else error.message
        if error.original_exception:
            msg += f" | Caused by: {str(error.original_exception)}"
        logger.error(msg)
    else:
        # Unexpected error
        msg = f"{context}: Unexpected error: {str(error)}" if context else f"Unexpected error: {str(error)}"
        logger.exception(msg)
