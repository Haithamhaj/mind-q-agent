import logging
from typing import Dict, Any, Optional
from datetime import datetime

from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.learning.decay_math import calculate_decay, calculate_days_since

logger = logging.getLogger(__name__)

class DecayJob:
    """
    Batch job to apply temporal decay to all graph edge weights.
    
    Should be run periodically (e.g., daily) via scheduler.
    """
    
    def __init__(self, graph_db: KuzuGraphDB, config: Optional[Dict[str, Any]] = None):
        self.graph_db = graph_db
        self.config = config

    def run(self) -> int:
        """
        Execute decay on all RELATED_TO edges.
        
        Returns:
            Number of edges updated.
        """
        logger.info("Starting decay batch job...")
        
        # 1. Query all RELATED_TO edges with weight and last_updated
        query = """
            MATCH ()-[r:RELATED_TO]->()
            RETURN id(r) AS edge_id, r.weight AS weight, r.last_updated AS last_updated
        """
        
        try:
            results = self.graph_db.execute(query, {})
        except Exception as e:
            logger.error(f"Failed to query edges for decay: {e}")
            return 0
        
        updated_count = 0
        
        for row in results:
            edge_id = row[0]
            current_weight = row[1] if row[1] is not None else 0.5
            last_updated = row[2]
            
            # Calculate days since last update
            if last_updated:
                days_since = calculate_days_since(str(last_updated))
            else:
                days_since = 0.0
            
            # Skip if less than 1 day (avoid excessive updates)
            if days_since < 1.0:
                continue
            
            # Calculate decayed weight
            new_weight = calculate_decay(current_weight, days_since, config=self.config)
            
            # Update if changed significantly
            if abs(new_weight - current_weight) > 0.001:
                try:
                    update_query = """
                        MATCH ()-[r:RELATED_TO]->()
                        WHERE id(r) = $edge_id
                        SET r.weight = $new_weight, r.last_updated = timestamp()
                    """
                    self.graph_db.execute(update_query, {"edge_id": edge_id, "new_weight": new_weight})
                    updated_count += 1
                    logger.debug(f"Decayed edge {edge_id}: {current_weight:.3f} -> {new_weight:.3f}")
                except Exception as e:
                    logger.warning(f"Failed to update edge {edge_id}: {e}")
        
        logger.info(f"Decay job complete. Updated {updated_count} edges.")
        return updated_count
