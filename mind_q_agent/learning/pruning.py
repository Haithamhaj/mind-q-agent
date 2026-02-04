import logging
from typing import List, Dict, Any, Optional

from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.config.manager import ConfigManager

logger = logging.getLogger(__name__)

def get_learning_config() -> Dict[str, Any]:
    """Retrieve learning configuration safely."""
    return ConfigManager.get_config().get("learning", {})

def get_edges_to_prune(graph_db: KuzuGraphDB, threshold: Optional[float] = None) -> List[int]:
    """
    Find edges with weight below threshold.
    
    Args:
        graph_db: KùzuDB graph instance.
        threshold: Weight threshold. Edges below this are prunable.
        
    Returns:
        List of edge IDs to prune.
    """
    if threshold is None:
        config = get_learning_config()
        threshold = float(config.get("prune_threshold", 0.1))
    
    query = """
        MATCH ()-[r:RELATED_TO]->()
        WHERE r.weight < $threshold
        RETURN id(r) AS edge_id
    """
    
    try:
        results = graph_db.execute(query, {"threshold": threshold})
        edge_ids = [row[0] for row in results]
        logger.info(f"Found {len(edge_ids)} edges below threshold {threshold}")
        return edge_ids
    except Exception as e:
        logger.error(f"Failed to query edges for pruning: {e}")
        return []

def prune_edges(graph_db: KuzuGraphDB, edge_ids: List[int]) -> int:
    """
    Delete edges by their IDs.
    
    Args:
        graph_db: KùzuDB graph instance.
        edge_ids: List of edge IDs to delete.
        
    Returns:
        Number of edges deleted.
    """
    if not edge_ids:
        return 0
    
    deleted_count = 0
    
    for edge_id in edge_ids:
        try:
            delete_query = """
                MATCH ()-[r:RELATED_TO]->()
                WHERE id(r) = $edge_id
                DELETE r
            """
            graph_db.execute(delete_query, {"edge_id": edge_id})
            deleted_count += 1
        except Exception as e:
            logger.warning(f"Failed to delete edge {edge_id}: {e}")
    
    logger.info(f"Pruned {deleted_count} edges from graph.")
    return deleted_count
