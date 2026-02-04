"""
Unit tests for KùzuDB Graph Database Interface.

Tests all functionality of the KuzuGraphDB class including schema creation,
CRUD operations, and error handling.
"""

import pytest
from pathlib import Path
from datetime import datetime

from mind_q_agent.graph.kuzu_graph import KuzuGraphDB


class TestKuzuGraphDB:
    """Test suite for KuzuGraphDB class."""
    
    @pytest.fixture
    def graph_db(self, tmp_path):
        """
        Create a temporary graph database for testing.
        
        Args:
            tmp_path: pytest tmp_path fixture
            
        Yields:
            KuzuGraphDB instance
        """
        db_path = tmp_path / "test_graph.db"
        graph = KuzuGraphDB(str(db_path))
        yield graph
        graph.close()
    
    def test_initialization(self, tmp_path):
        """Test database initialization and schema creation."""
        db_path = tmp_path / "init_test.db"
        graph = KuzuGraphDB(str(db_path))
        
        # Verify database file was created
        assert db_path.exists()
        
        # Verify connection is active
        assert graph.db is not None
        assert graph.conn is not None
        
        graph.close()
    
    def test_create_concept_valid(self, graph_db):
        """Test creating a valid concept."""
        embedding = [0.1] * 384
        
        graph_db.create_concept(
            name="Python",
            embedding=embedding,
            category="programming_language"
        )
        
        # Verify concept was created
        concept = graph_db.get_concept("Python")
        assert concept is not None
        assert concept['name'] == "Python"
        assert concept['category'] == "programming_language"
        assert concept['global_frequency'] == 1
        assert concept['is_broad'] == False
    
    def test_create_concept_invalid_embedding_dimension(self, graph_db):
        """Test that creating a concept with wrong embedding dimension fails."""
        invalid_embedding = [0.1] * 100  # Wrong dimension
        
        with pytest.raises(ValueError, match="must be 384-dimensional"):
            graph_db.create_concept(
                name="Invalid",
                embedding=invalid_embedding
            )
    
    def test_create_concept_default_category(self, graph_db):
        """Test creating a concept with default category."""
        embedding = [0.2] * 384
        
        graph_db.create_concept(name="TestConcept", embedding=embedding)
        
        concept = graph_db.get_concept("TestConcept")
        assert concept['category'] == "general"
    
    def test_get_concept_not_found(self, graph_db):
        """Test retrieving a non-existent concept."""
        result = graph_db.get_concept("NonExistent")
        assert result is None
    
    def test_create_edge_valid(self, graph_db):
        """Test creating a valid edge between concepts."""
        # Create two concepts first
        embedding_a = [0.1] * 384
        embedding_b = [0.2] * 384
        
        graph_db.create_concept("Python", embedding_a, "programming_language")
        graph_db.create_concept("Django", embedding_b, "framework")
        
        # Create edge
        graph_db.create_edge("Python", "Django", 0.8)
        
        # Verify edge exists
        query = """
            MATCH (a:Concept {name: 'Python'})-[r:RELATED_TO]->(b:Concept {name: 'Django'})
            RETURN r.base_weight as weight, r.sample_size as sample_size
        """
        result = graph_db.execute(query)
        
        assert not result.empty
        assert result.iloc[0]['weight'] == 0.8
        assert result.iloc[0]['sample_size'] == 1
    
    def test_create_edge_invalid_weight(self, graph_db):
        """Test that creating an edge with invalid weight fails."""
        embedding = [0.1] * 384
        graph_db.create_concept("A", embedding)
        graph_db.create_concept("B", embedding)
        
        # Test weight > 1
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            graph_db.create_edge("A", "B", 1.5)
        
        # Test weight < 0
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            graph_db.create_edge("A", "B", -0.5)
    
    def test_create_edge_nonexistent_concepts(self, graph_db):
        """Test behavior when creating an edge between nonexistent concepts."""
        initial_count = graph_db.get_edge_count()
        # KùzuDB silently skips creating edge if concepts don't exist
        graph_db.create_edge("NonExistent1", "NonExistent2", 0.5)
        # Edge count should remain the same
        assert graph_db.get_edge_count() == initial_count
    
    def test_get_node_count(self, graph_db):
        """Test counting nodes in the graph."""
        # Initially should be 0
        assert graph_db.get_node_count() == 0
        
        # Add some concepts
        embedding = [0.1] * 384
        graph_db.create_concept("Concept1", embedding)
        graph_db.create_concept("Concept2", embedding)
        graph_db.create_concept("Concept3", embedding)
        
        # Should now have 3 nodes
        assert graph_db.get_node_count() == 3
    
    def test_get_edge_count(self, graph_db):
        """Test counting edges in the graph."""
        # Initially should be 0
        assert graph_db.get_edge_count() == 0
        
        # Create concepts and edges
        embedding = [0.1] * 384
        graph_db.create_concept("A", embedding)
        graph_db.create_concept("B", embedding)
        graph_db.create_concept("C", embedding)
        
        graph_db.create_edge("A", "B", 0.5)
        graph_db.create_edge("B", "C", 0.7)
        
        # Should now have 2 edges
        assert graph_db.get_edge_count() == 2
    
    def test_execute_query_with_params(self, graph_db):
        """Test executing a parameterized query."""
        embedding = [0.1] * 384
        graph_db.create_concept("QueryTest", embedding, "test_category")
        
        query = "MATCH (c:Concept {category: $category}) RETURN c.name as name"
        result = graph_db.execute(query, {'category': 'test_category'})
        
        assert not result.empty
        assert result.iloc[0]['name'] == "QueryTest"
    
    def test_execute_query_returns_dataframe(self, graph_db):
        """Test that execute returns a pandas DataFrame."""
        import pandas as pd
        
        result = graph_db.execute("MATCH (n) RETURN count(n) as count")
        
        assert isinstance(result, pd.DataFrame)
        assert 'count' in result.columns
    
    def test_multiple_concepts_and_relationships(self, graph_db):
        """Test creating a more complex graph structure."""
        embedding = [0.1] * 384
        
        # Create a small knowledge graph
        concepts = [
            ("Python", "programming_language"),
            ("Django", "framework"),
            ("Flask", "framework"),
            ("REST", "concept"),
        ]
        
        for name, category in concepts:
            graph_db.create_concept(name, embedding, category)
        
        # Create relationships
        edges = [
            ("Python", "Django", 0.9),
            ("Python", "Flask", 0.8),
            ("Django", "REST", 0.7),
            ("Flask", "REST", 0.6),
        ]
        
        for a, b, weight in edges:
            graph_db.create_edge(a, b, weight)
        
        # Verify counts
        assert graph_db.get_node_count() == 4
        assert graph_db.get_edge_count() == 4
        
        # Verify we can query the graph
        query = """
            MATCH (p:Concept {name: 'Python'})-[r:RELATED_TO]->(f)
            RETURN f.name as framework, r.base_weight as weight
            ORDER BY r.base_weight DESC
        """
        result = graph_db.execute(query)
        
        assert len(result) == 2
        assert result.iloc[0]['framework'] == "Django"
        assert result.iloc[0]['weight'] == 0.9
    
    def test_concept_with_special_characters(self, graph_db):
        """Test creating concepts with special characters in names."""
        embedding = [0.1] * 384
        
        special_names = [
            "C++",
            "C#",
            "Object-Oriented Programming",
            "Machine Learning (ML)",
        ]
        
        for name in special_names:
            graph_db.create_concept(name, embedding)
            retrieved = graph_db.get_concept(name)
            assert retrieved is not None
            assert retrieved['name'] == name
    
    def test_edge_properties_initialization(self, graph_db):
        """Test that edge properties are initialized correctly."""
        embedding = [0.1] * 384
        graph_db.create_concept("Source", embedding)
        graph_db.create_concept("Target", embedding)
        
        graph_db.create_edge("Source", "Target", 0.75)
        
        query = """
            MATCH (a:Concept {name: 'Source'})-[r:RELATED_TO]->(b:Concept {name: 'Target'})
            RETURN r
        """
        result = graph_db.execute(query)
        edge = result.iloc[0]['r']
        
        # Verify all edge properties
        assert edge['base_weight'] == 0.75
        assert edge['current_weight'] == 0.75
        assert edge['sample_size'] == 1
        assert edge['confidence'] == 0.5
        assert edge['observation_variance'] == 0.0
        assert edge['decay_rate'] == 0.01
        assert edge['last_accessed'] is not None
    
    def test_database_persistence(self, tmp_path):
        """Test that data persists across connections."""
        db_path = tmp_path / "persist_test.db"
        embedding = [0.1] * 384
        
        # Create and populate database
        graph1 = KuzuGraphDB(str(db_path))
        graph1.create_concept("Persistent", embedding, "test")
        graph1.close()
        
        # Reconnect and verify data exists
        graph2 = KuzuGraphDB(str(db_path))
        concept = graph2.get_concept("Persistent")
        assert concept is not None
        assert concept['name'] == "Persistent"
        graph2.close()
    
    def test_close_connection(self, graph_db):
        """Test closing the database connection."""
        # Should not raise any exceptions
        graph_db.close()
