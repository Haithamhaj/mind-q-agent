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
                    processed INTEGER DEFAULT 0,  -- 0=unprocessed, 1=processed
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

    @handle_exceptions(logger, default_return=-1)
    def log_search(self, query: str) -> int:
        """Log a user search query."""
        return self._insert_event("SEARCH", query=query)

    @handle_exceptions(logger, default_return=-1)
    def log_view(self, target_id: str, duration_sec: float) -> int:
        """Log a document or concept view."""
        return self._insert_event("VIEW", target_id=target_id, duration_sec=duration_sec)

    @handle_exceptions(logger, default_return=-1)
    def log_click(self, target_id: str) -> int:
        """Log a click on a result/node."""
        return self._insert_event("CLICK", target_id=target_id)

    def _insert_event(self, event_type: str, target_id: Optional[str] = None, 
                      query: Optional[str] = None, duration_sec: Optional[float] = None) -> int:
        """Internal helper to insert event thread-safely."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO interactions (event_type, target_id, query, duration_sec)
                    VALUES (?, ?, ?, ?)
                """, (event_type, target_id, query, duration_sec))
                conn.commit()
                return cursor.lastrowid

    @handle_exceptions(logger, default_return=[])
    def get_recent_interactions(self, limit: int = 100):
        """Retrieve recent interactions for learning cycles."""
        with self._lock:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM interactions 
                    ORDER BY timestamp DESC, id DESC 
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]

    @handle_exceptions(logger, default_return=[])
    def get_unprocessed_interactions(self, limit: int = 100):
        """Get interactions not yet processed by Hebbian cycle."""
        with self._lock:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM interactions 
                    WHERE processed = 0
                    ORDER BY timestamp ASC, id ASC 
                    LIMIT ?
                """, (limit,))
                return [dict(row) for row in cursor.fetchall()]

    @handle_exceptions(logger)
    def mark_as_processed(self, event_ids):
        """Mark events as processed after Hebbian update."""
        if not event_ids:
            return
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                placeholders = ",".join("?" * len(event_ids))
                cursor.execute(f"""
                    UPDATE interactions SET processed = 1 WHERE id IN ({placeholders})
                """, event_ids)
                conn.commit()
