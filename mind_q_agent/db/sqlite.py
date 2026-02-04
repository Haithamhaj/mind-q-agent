
import sqlite3
import logging
from typing import Optional, Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class SQLiteDB:
    """
    Simple SQLite wrapper for storing key-value preferences and small structured data.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Create Preferences Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to init SQLite DB: {e}")
            raise

    def get_preference(self, key: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_all_preferences(self) -> Dict[str, str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM preferences")
            return {row[0]: row[1] for row in cursor.fetchall()}

    def set_preference(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO preferences (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
            """, (key, value))
            conn.commit()
