"""
Phase 1 End-to-End Integration Test

Tests the complete flow from file ingestion to search results.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

# Skip if dependencies not available
pytest.importorskip("kuzu")
pytest.importorskip("chromadb")


class TestPhase1E2E:
    """End-to-end tests for Phase 1 MVP functionality."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sample_documents(self, temp_data_dir):
        """Create sample documents for testing."""
        docs_dir = Path(temp_data_dir) / "documents"
        docs_dir.mkdir()
        
        # Create sample markdown files
        (docs_dir / "machine_learning.md").write_text("""
# Machine Learning Basics

Machine learning is a subset of artificial intelligence that enables 
systems to learn from data. Neural networks are a key component.

## Key Concepts
- Supervised Learning
- Unsupervised Learning
- Reinforcement Learning
        """)
        
        (docs_dir / "deep_learning.md").write_text("""
# Deep Learning Guide

Deep learning uses neural networks with multiple layers.
It's particularly effective for image recognition and NLP tasks.

## Applications
- Computer Vision
- Natural Language Processing
- Speech Recognition
        """)
        
        return docs_dir

    def test_vector_db_add_and_search(self, temp_data_dir, sample_documents):
        """Test adding documents to vector DB and searching."""
        from mind_q_agent.vector.chroma_vector import ChromaVectorDB
        
        vector_path = str(Path(temp_data_dir) / "vector_db")
        vector_db = ChromaVectorDB(db_path=vector_path, collection_name="test_e2e")
        
        # Add documents
        docs = []
        ids = []
        metadatas = []
        for i, doc in enumerate(sample_documents.glob("*.md")):
            text = doc.read_text()
            docs.append(text)
            ids.append(f"doc_{i}")
            metadatas.append({"source": str(doc)})
        
        vector_db.add_documents(docs, metadatas, ids)
        
        # Verify count
        assert vector_db.count() == 2
        
        # Search
        results = vector_db.query_similar("machine learning neural networks", n_results=5)
        assert len(results) > 0

    def test_search_engine_integration(self, temp_data_dir, sample_documents):
        """Test search engine with vector store."""
        from mind_q_agent.vector.chroma_vector import ChromaVectorDB
        from mind_q_agent.search.engine import SearchEngine
        
        vector_path = str(Path(temp_data_dir) / "vector_db")
        vector_db = ChromaVectorDB(db_path=vector_path, collection_name="test_search")
        
        # Add documents
        docs = []
        ids = []
        metadatas = []
        for i, doc in enumerate(sample_documents.glob("*.md")):
            text = doc.read_text()
            docs.append(text)
            ids.append(f"doc_{i}")
            metadatas.append({"source": str(doc)})
        
        vector_db.add_documents(docs, metadatas, ids)
        
        # Search using SearchEngine
        search_engine = SearchEngine(vector_store=vector_db)
        results = search_engine.search("neural networks deep learning")
        
        # Verify results
        assert results is not None
        assert len(results) > 0
        
        # Check results have expected structure
        for result in results:
            assert "id" in result
            assert "text" in result

    def test_cli_help_command(self):
        """Test CLI shows help without error."""
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        # Should exit successfully and show help
        assert result.returncode == 0
        assert "Mind-Q" in result.stdout or "usage" in result.stdout.lower()

    def test_learning_components_integration(self, temp_data_dir):
        """Test learning components work together."""
        from mind_q_agent.learning.tracker import InteractionTracker
        from mind_q_agent.learning.hebbian_math import calculate_new_weight, calculate_interaction_score
        
        # Setup tracker
        db_path = str(Path(temp_data_dir) / "interactions.db")
        tracker = InteractionTracker(db_path=db_path)
        
        # Log interactions
        tracker.log_search("neural networks")
        tracker.log_click("doc_123")
        tracker.log_view("doc_456", duration_sec=30.0)
        
        # Verify logged
        events = tracker.get_recent_interactions(limit=10)
        assert len(events) == 3
        
        # Verify unprocessed retrieval
        unprocessed = tracker.get_unprocessed_interactions(limit=10)
        assert len(unprocessed) == 3
        
        # Test Hebbian math
        config = {"alpha": 0.1, "event_scores": {"CLICK": 1.0}}
        score = calculate_interaction_score("CLICK", config=config)
        assert score == 1.0
        
        new_weight = calculate_new_weight(0.5, score, config=config)
        assert new_weight > 0.5  # Weight should increase

    def test_graph_db_basic_operations(self, temp_data_dir):
        """Test KuzuGraphDB basic operations."""
        from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
        
        graph_db = KuzuGraphDB(db_path=str(Path(temp_data_dir) / "graph"))
        
        # Create concept
        embedding = [0.1] * 384
        graph_db.create_concept("Test Concept", embedding, "test")
        
        # Retrieve concept
        concept = graph_db.get_concept("Test Concept")
        assert concept is not None
        assert concept["name"] == "Test Concept"
        
        # Verify node count
        count = graph_db.get_node_count()
        assert count >= 1
        
        graph_db.close()
