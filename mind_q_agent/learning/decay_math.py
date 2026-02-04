import math
import logging
from typing import Dict, Any, Optional

from mind_q_agent.config.manager import ConfigManager

logger = logging.getLogger(__name__)

def get_learning_config() -> Dict[str, Any]:
    """Retrieve learning configuration safely."""
    return ConfigManager.get_config().get("learning", {})

def calculate_decay(current_weight: float, days_since_update: float, config: Optional[Dict[str, Any]] = None) -> float:
    """
    Apply temporal decay to an edge weight.
    
    Formula: w_new = w_old * exp(-λ * Δt)
    
    Args:
        current_weight: Current edge weight (0.0 to 1.0).
        days_since_update: Number of days since last update.
        config: Config dict containing 'decay_rate' (λ).
        
    Returns:
        New decayed weight (always >= 0.0).
    """
    if config is None:
        config = get_learning_config()
        
    decay_rate = float(config.get("decay_rate", 0.05))
    
    if days_since_update <= 0:
        return current_weight
    
    # Exponential decay: w * e^(-λ * Δt)
    decay_factor = math.exp(-decay_rate * days_since_update)
    new_weight = current_weight * decay_factor
    
    # Ensure non-negative (should be by math, but safe)
    return max(0.0, new_weight)

def calculate_days_since(timestamp_str: str) -> float:
    """
    Calculate days elapsed since a timestamp string.
    
    Args:
        timestamp_str: ISO format or SQLite datetime string.
        
    Returns:
        Days elapsed as float.
    """
    from datetime import datetime
    
    try:
        # Handle SQLite CURRENT_TIMESTAMP format: YYYY-MM-DD HH:MM:SS
        if "T" in timestamp_str:
            dt = datetime.fromisoformat(timestamp_str)
        else:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        
        now = datetime.now()
        delta = now - dt
        return delta.total_seconds() / 86400.0  # Convert to days
        
    except Exception as e:
        logger.warning(f"Could not parse timestamp '{timestamp_str}': {e}")
        return 0.0
