import sqlite3
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class AutomationStorage:
    """Storage for automation metadata"""
    
    def __init__(self, db_path: str = "data/automation.db"):
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize database schema"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS automations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    workflow_id TEXT NOT NULL,
                    workflow_name TEXT NOT NULL,
                    description TEXT,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_execution TIMESTAMP,
                    execution_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """)
            
    def create_automation(self, automation_id: str, user_id: str, workflow_id: str, 
                         workflow_name: str, description: str, metadata: Dict = None):
        """Register a new automation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO automations 
                (id, user_id, workflow_id, workflow_name, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                automation_id, user_id, workflow_id, workflow_name, 
                description, json.dumps(metadata or {})
            ))
            
    def get_automation(self, automation_id: str) -> Optional[Dict]:
        """Get automation details"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM automations WHERE id = ?", (automation_id,))
            row = cursor.fetchone()
            
            if row:
                data = dict(row)
                data['metadata'] = json.loads(data['metadata']) if data['metadata'] else {}
                return data
            return None
            
    def list_user_automations(self, user_id: str) -> List[Dict]:
        """List all automations for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM automations WHERE user_id = ? ORDER BY created_at DESC", 
                (user_id,)
            )
            
            results = []
            for row in cursor:
                data = dict(row)
                data['metadata'] = json.loads(data['metadata']) if data['metadata'] else {}
                results.append(data)
            return results
            
    def update_status(self, automation_id: str, active: bool):
        """Update active status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE automations SET active = ? WHERE id = ?",
                (1 if active else 0, automation_id)
            )
            
    def log_execution(self, automation_id: str, timestamp: datetime = None):
        """Log an execution occurrence"""
        timestamp = timestamp or datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE automations 
                SET last_execution = ?, execution_count = execution_count + 1
                WHERE id = ?
            """, (timestamp, automation_id))
