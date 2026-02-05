import logging
import sqlite3
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LearningProgressService:
    """
    Learning Progress Tracker (Task 84).
    Tracks learning goals and concept mastery.
    """
    def __init__(self, db_path: str = "./data/learning.db"):
        self.db_path = Path(db_path)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Initialize database for goals and mastery"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Goals Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT DEFAULT 'active', -- active, completed
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Mastery Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mastery (
                    user_id TEXT NOT NULL,
                    concept TEXT NOT NULL,
                    level INTEGER DEFAULT 0, -- 0-100
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, concept)
                )
            """)
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path), check_same_thread=False)

    def add_goal(self, user_id: str, title: str) -> int:
        """Add a new learning goal"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO goals (user_id, title) VALUES (?, ?)", 
                    (user_id, title)
                )
                conn.commit()
                return cursor.lastrowid

    def get_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user learning goals"""
        with self._lock:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM goals WHERE user_id = ?", (user_id,))
                return [dict(row) for row in cursor.fetchall()]

    def update_mastery(self, user_id: str, concept: str, increment: int = 5):
        """Update concept mastery level"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Check existing
                cursor.execute(
                    "SELECT level FROM mastery WHERE user_id = ? AND concept = ?", 
                    (user_id, concept)
                )
                row = cursor.fetchone()
                
                if row:
                    new_level = min(100, row[0] + increment)
                    cursor.execute("""
                        UPDATE mastery SET level = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND concept = ?
                    """, (new_level, user_id, concept))
                else:
                    new_level = min(100, increment)
                    cursor.execute("""
                        INSERT INTO mastery (user_id, concept, level)
                        VALUES (?, ?, ?)
                    """, (user_id, concept, new_level))
                conn.commit()

    def get_mastery(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all mastery levels"""
        with self._lock:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM mastery WHERE user_id = ? ORDER BY level DESC", 
                    (user_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
