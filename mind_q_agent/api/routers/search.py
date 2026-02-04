from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging

from mind_q_agent.search.engine import SearchEngine
from mind_q_agent.vector.chroma_vector import ChromaVectorDB
from mind_q_agent.api.settings import settings

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

logger = logging.getLogger(__name__)

# Singleton wrapper
try:
    vector_db = ChromaVectorDB(settings.CHROMA_DB_PATH)
    search_engine = SearchEngine(vector_db)
except Exception as e:
    logger.error(f"Failed to initialize Search Engine: {e}")
    search_engine = None

@router.get("/", response_model=List[Dict[str, Any]])
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=50, description="Max results")
):
    """
    Perform semantic search on the knowledge base.
    """
    if not search_engine:
        raise HTTPException(status_code=500, detail="Search engine not initialized")
    
    try:
        results = search_engine.search(q, limit=limit)
        return results
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
