import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict

from mind_q_agent.learning.tracker import InteractionTracker
from mind_q_agent.learning.hebbian_math import calculate_interaction_score, calculate_new_weight
from mind_q_agent.graph.kuzu_graph import KuzuGraphDB

logger = logging.getLogger(__name__)

class HebbianUpdater:
    """
    Applies Hebbian learning to graph edges based on logged interactions.
    
    Workflow:
    1. Fetch unprocessed interactions from tracker.
    2. Group by target_id (concept or document hash).
    3. For each target, find related edges in graph.
    4. Apply weight update formula.
    5. Mark interactions as processed.
    """
    
    def __init__(self, tracker: InteractionTracker, graph_db: KuzuGraphDB, config: Optional[Dict[str, Any]] = None):
        self.tracker = tracker
        self.graph_db = graph_db
        self.config = config

    def run_update_cycle(self, batch_size: int = 100) -> int:
        """
        Execute one cycle of Hebbian weight updates.
        
        Returns:
            Number of interactions processed.
        """
        # 1. Fetch unprocessed interactions
        interactions = self.tracker.get_unprocessed_interactions(limit=batch_size)
        if not interactions:
            logger.debug("No unprocessed interactions found.")
            return 0
        
        logger.info(f"Processing {len(interactions)} interactions for Hebbian update.")
        
        # 2. Group by target_id
        grouped = defaultdict(list)
        for event in interactions:
            target = event.get("target_id")
            if target:
                grouped[target].append(event)
        
        # 3. Process each target
        processed_ids = []
        for target_id, events in grouped.items():
            try:
                self._update_edges_for_target(target_id, events)
                processed_ids.extend([e["id"] for e in events])
            except Exception as e:
                logger.warning(f"Failed to update edges for {target_id}: {e}")
        
        # 4. Mark as processed
        self.tracker.mark_as_processed(processed_ids)
        logger.info(f"Hebbian cycle complete. Processed {len(processed_ids)} interactions.")
        
        return len(processed_ids)

    def _update_edges_for_target(self, target_id: str, events: List[Dict[str, Any]]):
        """Update edge weights for a specific target."""
        # Calculate aggregate interaction score
        total_score = 0.0
        for event in events:
            score = calculate_interaction_score(
                event.get("event_type", ""),
                duration_sec=event.get("duration_sec", 0.0) or 0.0,
                config=self.config
            )
            total_score += score
        
        # Normalize score (cap at 1.0 for single cycle)
        interaction_score = min(1.0, total_score)
        
        # Find edges involving this target (as Concept)
        # Query: MATCH (c:Concept {name: $target})-[r:RELATED_TO]-() RETURN r.weight, id(r)
        query = """
            MATCH (c:Concept {name: $target})-[r:RELATED_TO]-()
            RETURN id(r) AS edge_id, r.weight AS current_weight
        """
        
        try:
            results = self.graph_db.execute(query, {"target": target_id})
            
            for row in results:
                edge_id = row[0]
                current_weight = row[1] if row[1] is not None else 0.5  # Default weight
                
                new_weight = calculate_new_weight(current_weight, interaction_score, config=self.config)
                
                # Update edge weight
                update_query = """
                    MATCH ()-[r:RELATED_TO]->()
                    WHERE id(r) = $edge_id
                    SET r.weight = $new_weight
                """
                self.graph_db.execute(update_query, {"edge_id": edge_id, "new_weight": new_weight})
                
                logger.debug(f"Updated edge {edge_id}: {current_weight:.3f} -> {new_weight:.3f}")
                
        except Exception as e:
            logger.error(f"Error updating edges for target {target_id}: {e}")
            raise
