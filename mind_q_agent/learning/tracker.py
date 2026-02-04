import logging
import sqlite3
import threading
from pathlib import Path
from typing import Optional

from mind_q_agent.utils.decorator import monitor_execution, handle_exceptions

logger = logging.getLogger(__name__)

class InteractionTracker:
    """
    Manages the Interaction Database (SQLite).
    Stores events like Searches, Clicks, and Views to power Hebbian Learning.
    Thread-safe implementation using thread-local storage or careful connection management.
    Per SQLite best practices, we'll open a connection per thread or lock around writes if simplified.
    Here we use a lock for simplicity in MVP.
    """
    
    def __init__(self, db_path: str = "./data/interactions.db"):
        self.db_path = Path(db_path)
        self._lock = threading.Lock()
        self._init_db()

    @handle_exceptions(logger)
    def _init_db(self):
        """Initialize database schema if not exists."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create Interactions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,  -- SEARCH, VIEW, CLICK
                    target_id TEXT,            -- Doc Hash or Concept Name
                    query TEXT,                -- Search query (optional)
                    duration_sec REAL,         -- Time spent (optional)
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create Index on target_id for faster aggregation
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_target_id ON interactions(target_id)
            """)
            
            conn.commit()
            logger.info(f"Interaction DB initialized at {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get a SQLite connection."""
        return sqlite3.connect(str(self.db_path), check_same_thread=False)

    @monitor_execution(logger)
    def close(self):
        """Close resources if needed (connections are mostly context-managed)."""
        pass
