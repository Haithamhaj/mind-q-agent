"""
Hierarchy Classifier for Knowledge Graph.

Classifies concepts as root, branch, or leaf based on connectivity.
"""

import logging
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class HierarchyLevel(Enum):
    """Concept hierarchy levels."""
    ROOT = "root"       # High connectivity, abstract
    BRANCH = "branch"   # Medium connectivity
    LEAF = "leaf"       # Low connectivity, specific


def classify_concept(
    in_degree: int,
    out_degree: int,
    total_concepts: int,
    config: Optional[Dict[str, Any]] = None
) -> HierarchyLevel:
    """
    Classify a concept based on its connectivity.
    
    Args:
        in_degree: Number of incoming edges.
        out_degree: Number of outgoing edges.
        total_concepts: Total concepts in graph (for normalization).
        config: Optional configuration.
        
    Returns:
        HierarchyLevel classification.
    """
    cfg = config or {}
    
    # Thresholds (as percentage of total concepts)
    root_threshold = cfg.get("root_threshold", 0.1)  # 10% connections = root
    branch_threshold = cfg.get("branch_threshold", 0.02)  # 2% = branch
    
    total_degree = in_degree + out_degree
    
    if total_concepts == 0:
        return HierarchyLevel.LEAF
    
    connectivity_ratio = total_degree / total_concepts
    
    if connectivity_ratio >= root_threshold:
        return HierarchyLevel.ROOT
    elif connectivity_ratio >= branch_threshold:
        return HierarchyLevel.BRANCH
    else:
        return HierarchyLevel.LEAF


class HierarchyClassifier:
    """
    Classifies concepts into hierarchy levels.
    """
    
    def __init__(self, graph_db, config: Optional[Dict[str, Any]] = None):
        self.graph_db = graph_db
        self.config = config or {}
        self._total_concepts: Optional[int] = None

    def _get_total_concepts(self) -> int:
        """Get total concept count (cached)."""
        if self._total_concepts is None:
            try:
                result = self.graph_db.execute(
                    "MATCH (c:Concept) RETURN count(c) AS cnt", {}
                )
                self._total_concepts = int(result.iloc[0]['cnt']) if not result.empty else 0
            except Exception:
                self._total_concepts = 0
        return self._total_concepts

    def classify(self, concept_name: str) -> HierarchyLevel:
        """
        Classify a concept.
        
        Args:
            concept_name: Name of the concept.
            
        Returns:
            HierarchyLevel for the concept.
        """
        try:
            # Count in-degree
            in_query = """
                MATCH ()-[r:RELATED_TO]->(c:Concept {name: $name})
                RETURN count(r) AS cnt
            """
            in_result = self.graph_db.execute(in_query, {"name": concept_name})
            in_degree = int(in_result.iloc[0]['cnt']) if not in_result.empty else 0
            
            # Count out-degree
            out_query = """
                MATCH (c:Concept {name: $name})-[r:RELATED_TO]->()
                RETURN count(r) AS cnt
            """
            out_result = self.graph_db.execute(out_query, {"name": concept_name})
            out_degree = int(out_result.iloc[0]['cnt']) if not out_result.empty else 0
            
            total = self._get_total_concepts()
            
            return classify_concept(in_degree, out_degree, total, self.config)
            
        except Exception as e:
            logger.error(f"Failed to classify {concept_name}: {e}")
            return HierarchyLevel.LEAF

    def classify_all(self) -> Dict[str, HierarchyLevel]:
        """
        Classify all concepts in the graph.
        
        Returns:
            Dictionary mapping concept names to hierarchy levels.
        """
        result = {}
        
        try:
            concepts = self.graph_db.execute(
                "MATCH (c:Concept) RETURN c.name AS name", {}
            )
            
            for _, row in concepts.iterrows():
                name = row['name']
                result[name] = self.classify(name)
                
        except Exception as e:
            logger.error(f"Failed to classify all concepts: {e}")
            
        return result
