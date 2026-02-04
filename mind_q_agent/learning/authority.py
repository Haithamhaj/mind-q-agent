"""
Authority Scorer for Sources.

Calculates and manages authority scores for knowledge sources.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from mind_q_agent.config.manager import ConfigManager

logger = logging.getLogger(__name__)


def calculate_authority_score(
    source_type: str,
    base_scores: Optional[Dict[str, float]] = None,
    modifiers: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate authority score for a source.
    
    Args:
        source_type: Type of source (file extension or domain).
        base_scores: Base authority scores by type.
        modifiers: Additional modifiers.
        
    Returns:
        Authority score (0.0 to 1.0).
    """
    # Default base scores
    defaults = {
        ".pdf": 0.8,      # Academic papers
        ".md": 0.7,       # Technical docs
        ".txt": 0.5,      # Plain text
        ".docx": 0.6,     # Word docs
        "arxiv.org": 0.9,      # Academic
        "wikipedia.org": 0.7,  # Encyclopedia
        "github.com": 0.7,     # Code/docs
        "medium.com": 0.5,     # Blogs
        "default": 0.5
    }
    
    scores = base_scores if base_scores else defaults
    
    # Find matching score
    source_lower = source_type.lower()
    
    for key, score in scores.items():
        if key in source_lower:
            base = score
            break
    else:
        base = scores.get("default", 0.5)
    
    # Apply modifiers
    if modifiers:
        for mod_key, mod_value in modifiers.items():
            if mod_key in source_lower:
                base = base * mod_value
    
    return max(0.0, min(1.0, base))


class AuthorityScorer:
    """
    Authority scoring component for sources.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config()
        self.base_scores = self.config.get("base_scores", {})
        self.modifiers = self.config.get("modifiers", {})
        self._source_history: Dict[str, List[float]] = {}

    def _load_config(self) -> Dict[str, Any]:
        """Load authority config."""
        try:
            return ConfigManager.get_config().get("authority", {})
        except Exception:
            return {}

    def score(self, source: str) -> float:
        """
        Get authority score for a source.
        
        Args:
            source: Source identifier (path or URL).
            
        Returns:
            Authority score (0.0 to 1.0).
        """
        return calculate_authority_score(
            source, self.base_scores, self.modifiers
        )

    def record_verification(self, source: str, was_accurate: bool):
        """
        Record a verification result for a source.
        
        Args:
            source: Source identifier.
            was_accurate: Whether the source was accurate.
        """
        if source not in self._source_history:
            self._source_history[source] = []
        
        self._source_history[source].append(1.0 if was_accurate else 0.0)
        
        # Limit history size
        if len(self._source_history[source]) > 100:
            self._source_history[source] = self._source_history[source][-100:]

    def get_historical_score(self, source: str) -> Optional[float]:
        """
        Get authority score based on verification history.
        
        Args:
            source: Source identifier.
            
        Returns:
            Historical accuracy score, or None if no history.
        """
        history = self._source_history.get(source)
        
        if not history:
            return None
        
        return sum(history) / len(history)

    def get_combined_score(self, source: str) -> float:
        """
        Get combined authority score (base + historical).
        
        Args:
            source: Source identifier.
            
        Returns:
            Combined authority score.
        """
        base = self.score(source)
        historical = self.get_historical_score(source)
        
        if historical is None:
            return base
        
        # Weighted average (50% base, 50% historical)
        return 0.5 * base + 0.5 * historical
