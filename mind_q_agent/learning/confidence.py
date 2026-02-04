"""
Confidence Score Logic for Knowledge Graph.

Calculates confidence scores for concepts based on multiple factors.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def calculate_confidence_score(
    edge_weight: float = 0.5,
    source_authority: float = 0.5,
    recency_days: float = 0.0,
    corroboration_count: int = 1,
    config: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculate confidence score for a concept/relationship.
    
    Combines multiple factors:
    - Edge weight (how often co-occurred)
    - Source authority (trustworthiness)
    - Recency (newer is better)
    - Corroboration (multiple sources agree)
    
    Args:
        edge_weight: Current edge weight (0.0 to 1.0).
        source_authority: Authority score of source (0.0 to 1.0).
        recency_days: Days since last update.
        corroboration_count: Number of sources confirming this.
        config: Optional configuration overrides.
        
    Returns:
        Confidence score (0.0 to 1.0).
    """
    cfg = config or {}
    
    # Weights for each factor (should sum to 1.0)
    w_edge = cfg.get("weight_edge", 0.3)
    w_authority = cfg.get("weight_authority", 0.3)
    w_recency = cfg.get("weight_recency", 0.2)
    w_corroboration = cfg.get("weight_corroboration", 0.2)
    
    # Recency factor (exponential decay)
    decay_rate = cfg.get("recency_decay_rate", 0.05)
    recency_score = max(0.1, 1.0 - (recency_days * decay_rate))
    
    # Corroboration factor (logarithmic growth)
    import math
    corroboration_score = min(1.0, math.log10(corroboration_count + 1) / 2)
    
    # Weighted combination
    confidence = (
        w_edge * edge_weight +
        w_authority * source_authority +
        w_recency * recency_score +
        w_corroboration * corroboration_score
    )
    
    # Clamp to [0, 1]
    return max(0.0, min(1.0, confidence))


def calculate_concept_confidence(
    concept_name: str,
    graph_db,
    config: Optional[Dict[str, Any]] = None
) -> float:
    """
    Calculate confidence for a specific concept.
    
    Queries graph for edge weights and calculates aggregate confidence.
    
    Args:
        concept_name: Name of the concept.
        graph_db: KuzuGraphDB instance.
        config: Optional configuration.
        
    Returns:
        Confidence score (0.0 to 1.0).
    """
    try:
        # Query edges connected to this concept
        query = """
            MATCH (c:Concept {name: $name})-[r:RELATED_TO]-()
            RETURN r.weight AS weight, r.last_updated AS last_updated
        """
        results = graph_db.execute(query, {"name": concept_name})
        
        if results.empty:
            return 0.5  # Default confidence
        
        # Calculate average weight
        avg_weight = results['weight'].mean() if 'weight' in results.columns else 0.5
        
        # Count connections (corroboration)
        connection_count = len(results)
        
        return calculate_confidence_score(
            edge_weight=avg_weight,
            corroboration_count=connection_count,
            config=config
        )
        
    except Exception as e:
        logger.error(f"Failed to calculate confidence for {concept_name}: {e}")
        return 0.5


class ConfidenceScorer:
    """
    Confidence scoring component.
    
    Calculates and caches confidence scores for concepts.
    """
    
    def __init__(self, graph_db, config: Optional[Dict[str, Any]] = None):
        self.graph_db = graph_db
        self.config = config or {}
        self._cache: Dict[str, float] = {}

    def score(self, concept_name: str) -> float:
        """Get confidence score for a concept."""
        if concept_name in self._cache:
            return self._cache[concept_name]
            
        score = calculate_concept_confidence(
            concept_name, self.graph_db, self.config
        )
        self._cache[concept_name] = score
        return score

    def clear_cache(self):
        """Clear the confidence cache."""
        self._cache.clear()
