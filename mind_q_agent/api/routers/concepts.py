from fastapi import APIRouter, HTTPException, Path
import logging
from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.api.settings import settings

router = APIRouter(
    prefix="/concepts",
    tags=["concepts"]
)

logger = logging.getLogger(__name__)

# Singleton
try:
    graph_db = KuzuGraphDB(settings.KUZU_DB_PATH)
except Exception as e:
    logger.error(f"Failed to initialize Graph DB: {e}")
    graph_db = None

@router.post("/{name}/boost")
def boost_concept(name: str = Path(..., description="Concept name")):
    """
    Boost a concept's global frequency.
    """
    if not graph_db:
        raise HTTPException(status_code=500, detail="Graph DB not initialized")
    
    try:
        # Check if concept exists first
        concept = graph_db.get_concept(name)
        if not concept:
             raise HTTPException(status_code=404, detail=f"Concept '{name}' not found")
             
        graph_db.boost_concept(name)
        return {"message": f"Concept '{name}' boosted successfully", "concept": name}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Boost failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{name}/mute")
def mute_concept(name: str = Path(..., description="Concept name")):
    """
    Mute a concept (set is_ignored=true).
    """
    if not graph_db:
        raise HTTPException(status_code=500, detail="Graph DB not initialized")
    
    try:
        # Check if concept exists
        concept = graph_db.get_concept(name)
        if not concept:
             raise HTTPException(status_code=404, detail=f"Concept '{name}' not found")

        graph_db.mute_concept(name)
        return {"message": f"Concept '{name}' muted successfully", "concept": name}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mute failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
