"""Unit tests for confidence, hierarchy, cluster, and authority."""

import pytest
from unittest.mock import MagicMock
import pandas as pd


class TestConfidenceScoring:
    """Tests for confidence scoring."""

    def test_calculate_confidence_default(self):
        from mind_q_agent.learning.confidence import calculate_confidence_score
        
        score = calculate_confidence_score()
        
        assert 0.0 <= score <= 1.0

    def test_confidence_increases_with_weight(self):
        from mind_q_agent.learning.confidence import calculate_confidence_score
        
        low = calculate_confidence_score(edge_weight=0.2)
        high = calculate_confidence_score(edge_weight=0.9)
        
        assert high > low

    def test_confidence_increases_with_corroboration(self):
        from mind_q_agent.learning.confidence import calculate_confidence_score
        
        single = calculate_confidence_score(corroboration_count=1)
        multiple = calculate_confidence_score(corroboration_count=10)
        
        assert multiple > single


class TestHierarchyClassifier:
    """Tests for hierarchy classification."""

    def test_classify_leaf(self):
        from mind_q_agent.learning.hierarchy import classify_concept, HierarchyLevel
        
        # With very low connectivity relative to graph size
        level = classify_concept(in_degree=0, out_degree=1, total_concepts=100)
        
        assert level == HierarchyLevel.LEAF

    def test_classify_root(self):
        from mind_q_agent.learning.hierarchy import classify_concept, HierarchyLevel
        
        level = classify_concept(in_degree=50, out_degree=50, total_concepts=100)
        
        assert level == HierarchyLevel.ROOT


class TestClusterDetection:
    """Tests for cluster detection."""

    def test_find_clusters_empty(self):
        from mind_q_agent.learning.cluster import find_clusters_simple
        
        clusters = find_clusters_simple([])
        
        assert clusters == []

    def test_find_clusters_single_component(self):
        from mind_q_agent.learning.cluster import find_clusters_simple
        
        edges = [("a", "b"), ("b", "c"), ("c", "d")]
        clusters = find_clusters_simple(edges, min_cluster_size=2)
        
        assert len(clusters) == 1
        assert len(clusters[0]) == 4

    def test_find_clusters_multiple_components(self):
        from mind_q_agent.learning.cluster import find_clusters_simple
        
        edges = [("a", "b"), ("c", "d")]  # Two disconnected pairs
        clusters = find_clusters_simple(edges, min_cluster_size=2)
        
        assert len(clusters) == 2


class TestAuthorityScorer:
    """Tests for authority scoring."""

    def test_score_pdf_high(self):
        from mind_q_agent.learning.authority import calculate_authority_score
        
        score = calculate_authority_score(".pdf")
        
        assert score >= 0.7

    def test_score_arxiv_highest(self):
        from mind_q_agent.learning.authority import calculate_authority_score
        
        score = calculate_authority_score("arxiv.org")
        
        assert score >= 0.9

    def test_authority_scorer_class(self):
        from mind_q_agent.learning.authority import AuthorityScorer
        
        scorer = AuthorityScorer()
        
        score = scorer.score("document.pdf")
        assert 0.0 <= score <= 1.0

    def test_historical_scoring(self):
        from mind_q_agent.learning.authority import AuthorityScorer
        
        scorer = AuthorityScorer()
        
        # Record some verifications
        scorer.record_verification("test.com", was_accurate=True)
        scorer.record_verification("test.com", was_accurate=True)
        scorer.record_verification("test.com", was_accurate=False)
        
        historical = scorer.get_historical_score("test.com")
        
        assert historical is not None
        assert abs(historical - 0.666) < 0.1  # 2/3 accurate
