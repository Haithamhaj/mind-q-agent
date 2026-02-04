import functools
import time
from typing import Any, Callable, TypeVar

# Type var for return value
R = TypeVar("R")

def monitor_execution(logger: Any) -> Callable:
    """
    Decorator to log execution time and entry/exit of methods.
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> R:
            logger.debug(f"Entering {func.__name__}")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"Exiting {func.__name__} (Duration: {duration:.4f}s)")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Error in {func.__name__} after {duration:.4f}s: {e}")
                raise e
        return wrapper
    return decorator

def handle_exceptions(logger: Any, default_return: Any = None) -> Callable:
    """
    Decorator to catch exceptions, log them, and return a default value.
    Prevents crash but loses the exception details to the caller (use carefully).
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> R:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception handled in {func.__name__}: {e}", exc_info=True)
                return default_return
        return wrapper
    return decorator
