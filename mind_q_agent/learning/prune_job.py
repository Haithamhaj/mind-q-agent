import logging
from typing import Dict, Any, Optional

from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.learning.pruning import get_edges_to_prune, prune_edges

logger = logging.getLogger(__name__)

class PruneJob:
    """
    Batch job to prune weak edges from the graph.
    
    Should be run periodically (e.g., weekly) via scheduler.
    """
    
    def __init__(self, graph_db: KuzuGraphDB, config: Optional[Dict[str, Any]] = None):
        self.graph_db = graph_db
        self.config = config

    def run(self, threshold: Optional[float] = None) -> int:
        """
        Execute pruning job.
        
        Args:
            threshold: Optional override for prune threshold.
            
        Returns:
            Number of edges pruned.
        """
        logger.info("Starting prune job...")
        
        # Get edges to prune
        edge_ids = get_edges_to_prune(self.graph_db, threshold=threshold)
        
        if not edge_ids:
            logger.info("No edges to prune.")
            return 0
        
        # Delete them
        count = prune_edges(self.graph_db, edge_ids)
        
        logger.info(f"Prune job complete. Removed {count} edges.")
        return count
