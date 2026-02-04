from fastapi import APIRouter, HTTPException, Body
from typing import Dict
import logging
import os
from mind_q_agent.db.sqlite import SQLiteDB

router = APIRouter(
    prefix="/preferences",
    tags=["preferences"]
)

logger = logging.getLogger(__name__)

# Singleton wrapper
DB_PATH = os.path.join("data", "mind_q.sqlite")
try:
    os.makedirs("data", exist_ok=True)
    db = SQLiteDB(DB_PATH)
except Exception as e:
    logger.error(f"Failed to initialize SQLite DB: {e}")
    db = None

@router.get("/", response_model=Dict[str, str])
def get_preferences():
    """
    Get all user preferences.
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db.get_all_preferences()

@router.patch("/", response_model=Dict[str, str])
def update_preferences(prefs: Dict[str, str] = Body(...)):
    """
    Update user preferences (partial update).
    """
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        for k, v in prefs.items():
            db.set_preference(k, str(v))
        return db.get_all_preferences()
    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))
