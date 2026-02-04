import logging
from typing import Dict, Any, Optional

from mind_q_agent.config.manager import ConfigManager

logger = logging.getLogger(__name__)

def get_learning_config() -> Dict[str, Any]:
    """Retrieve learning configuration safely."""
    return ConfigManager.get_config().get("learning", {})

def calculate_interaction_score(event_type: str, duration_sec: float = 0.0, config: Optional[Dict[str, Any]] = None) -> float:
    """
    Calculate the 'Intensity' (I) of an interaction based on event type.
    
    Args:
        event_type: 'CLICK', 'VIEW', 'SEARCH', etc.
        duration_sec: Duration for VIEW events.
        config: Optional config dict override. Uses global config if None.
        
    Returns:
        Score between 0.0 and 1.0 (usually).
    """
    if config is None:
        config = get_learning_config()
        
    scores = config.get("event_scores", {})
    
    if event_type == "CLICK":
        return float(scores.get("CLICK", 1.0))
    
    elif event_type == "SEARCH":
        return float(scores.get("SEARCH", 0.5))
        
    elif event_type == "VIEW":
        base = float(scores.get("VIEW_BASE", 0.3))
        max_val = float(scores.get("VIEW_MAX", 1.0))
        # Simple logistic-like or capped linear growth for duration
        # Example: 30 seconds to reach max integration
        bonus = min(max_val - base, (duration_sec / 30.0) * (max_val - base))
        return base + max(0.0, bonus)
        
    return 0.1 # Default low score for unknown events

def calculate_new_weight(current_weight: float, interaction_score: float, config: Optional[Dict[str, Any]] = None) -> float:
    """
    Apply Hebbian Learning rule: w_new = w + alpha * (1 - w) * I
    
    Args:
        current_weight: Current edge weight (0.0 to 1.0).
        interaction_score: Intensity of the current interaction (I).
        config: Config dict containing 'alpha' (learning rate).
        
    Returns:
        New updated weight.
    """
    if config is None:
        config = get_learning_config()
        
    alpha = float(config.get("alpha", 0.1))
    
    # Hebbian-like Soft Clamp Formula
    # Ensures weight increases towards 1.0 but never exceeds it.
    delta = alpha * (1.0 - current_weight) * interaction_score
    
    return current_weight + delta
