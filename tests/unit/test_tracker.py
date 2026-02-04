import sqlite3
import pytest
from pathlib import Path
from mind_q_agent.learning.tracker import InteractionTracker

class TestInteractionTracker:
    """Unit tests for InteractionTracker."""

    @pytest.fixture
    def test_db_path(self, tmp_path):
        return tmp_path / "test_interactions.db"

    @pytest.fixture
    def tracker(self, test_db_path):
        return InteractionTracker(str(test_db_path))

    def test_init_db(self, tracker, test_db_path):
        """Test database and table creation."""
        assert test_db_path.exists()
        
        # Verify schema
        conn = sqlite3.connect(str(test_db_path))
        cursor = conn.cursor()
        
        # Check table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interactions'")
        assert cursor.fetchone() is not None
        
        # Check columns (pragma user_info is one way, or just insert)
        cursor.execute("PRAGMA table_info(interactions)")
        columns = {row[1] for row in cursor.fetchall()}
        expected_cols = {"id", "event_type", "target_id", "query", "duration_sec", "timestamp"}
        assert expected_cols.issubset(columns)
        
        conn.close()

    def test_manual_insert(self, tracker, test_db_path):
        """Test manually inserting a row via helper storage method (simulated)."""
        # Since we haven't implemented log methods (Task 22), we assume we can get a connection or we rely on _init_db
        # But wait, tracker doesn't expose write methods yet (Task 22). 
        # So we can only test that the DB is ready for writing via a raw connection.
        
        conn = sqlite3.connect(str(test_db_path))
        cursor = conn.cursor()
        cursor.execute("INSERT INTO interactions (event_type, target_id) VALUES (?, ?)", ("TEST", "hash1"))
        conn.commit()
        
        cursor.execute("SELECT * FROM interactions")
        row = cursor.fetchone()
        assert row is not None
        assert row[1] == "TEST"
        conn.close()
