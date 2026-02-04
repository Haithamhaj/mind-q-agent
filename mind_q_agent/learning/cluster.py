"""
Cluster Detection for Knowledge Graph.

Groups related concepts into clusters using community detection.
"""

import logging
from typing import Dict, Any, Optional, List, Set
from collections import defaultdict

logger = logging.getLogger(__name__)


def find_clusters_simple(
    edges: List[tuple],
    min_cluster_size: int = 2
) -> List[Set[str]]:
    """
    Simple connected components clustering.
    
    Uses union-find to identify connected components.
    
    Args:
        edges: List of (node1, node2) tuples.
        min_cluster_size: Minimum nodes for valid cluster.
        
    Returns:
        List of clusters (sets of node names).
    """
    if not edges:
        return []
    
    # Union-Find data structure
    parent = {}
    
    def find(x):
        if x not in parent:
            parent[x] = x
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
    
    # Process edges
    for n1, n2 in edges:
        union(n1, n2)
    
    # Group by parent
    clusters_dict = defaultdict(set)
    for node in parent:
        root = find(node)
        clusters_dict[root].add(node)
    
    # Filter by minimum size
    clusters = [c for c in clusters_dict.values() if len(c) >= min_cluster_size]
    
    return clusters


class ClusterDetector:
    """
    Cluster detection component for knowledge graph.
    """
    
    def __init__(self, graph_db, config: Optional[Dict[str, Any]] = None):
        self.graph_db = graph_db
        self.config = config or {}
        self.min_cluster_size = self.config.get("min_cluster_size", 2)

    def detect_clusters(self) -> List[Set[str]]:
        """
        Detect clusters in the concept graph.
        
        Returns:
            List of clusters (sets of concept names).
        """
        try:
            # Query all edges
            query = """
                MATCH (a:Concept)-[r:RELATED_TO]->(b:Concept)
                RETURN a.name AS source, b.name AS target
            """
            results = self.graph_db.execute(query, {})
            
            if results.empty:
                return []
            
            edges = [
                (row['source'], row['target'])
                for _, row in results.iterrows()
            ]
            
            return find_clusters_simple(edges, self.min_cluster_size)
            
        except Exception as e:
            logger.error(f"Failed to detect clusters: {e}")
            return []

    def get_cluster_for_concept(self, concept_name: str) -> Optional[Set[str]]:
        """
        Get the cluster containing a specific concept.
        
        Args:
            concept_name: Name of the concept.
            
        Returns:
            Set of concept names in the cluster, or None.
        """
        clusters = self.detect_clusters()
        
        for cluster in clusters:
            if concept_name in cluster:
                return cluster
                
        return None

    def get_cluster_stats(self) -> Dict[str, Any]:
        """
        Get statistics about clusters.
        
        Returns:
            Dictionary with cluster statistics.
        """
        clusters = self.detect_clusters()
        
        if not clusters:
            return {
                "total_clusters": 0,
                "avg_size": 0,
                "max_size": 0,
                "min_size": 0
            }
        
        sizes = [len(c) for c in clusters]
        
        return {
            "total_clusters": len(clusters),
            "avg_size": sum(sizes) / len(sizes),
            "max_size": max(sizes),
            "min_size": min(sizes)
        }
