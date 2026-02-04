"""
KùzuDB Graph Database Interface for Mind-Q Agent.

This module provides a production-ready interface to KùzuDB for managing
the knowledge graph including concepts, documents, and their relationships.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

import kuzu
import pandas as pd


logger = logging.getLogger(__name__)


class KuzuGraphDB:
    """
    KùzuDB Graph Database Interface.
    
    Manages the knowledge graph with concepts, documents, and relationships.
    Implements Hebbian learning through weighted edges that strengthen over time.
    
    Attributes:
        db_path: Path to the database directory
        db: KùzuDB database instance
        conn: Database connection
    """
    
    def __init__(self, db_path: str):
        """
        Initialize KùzuDB connection and create schema if needed.
        
        Args:
            db_path: Path to the database directory
            
        Raises:
            RuntimeError: If database initialization fails
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self.db = kuzu.Database(str(self.db_path))
            self.conn = kuzu.Connection(self.db)
            logger.info(f"Connected to KùzuDB at {self.db_path}")
            
            # Initialize schema
            self._create_schema()
            
        except Exception as e:
            logger.error(f"Failed to initialize KùzuDB: {e}")
            raise RuntimeError(f"Database initialization failed: {e}") from e
    
    def _create_schema(self) -> None:
        """
        Create database schema if it doesn't exist.
        
        Creates node tables for User, Document, and Concept,
        and relationship tables for RELATED_TO and DISCUSSES.
        """
        try:
            # Create User node table
            self._execute_safe("""
                CREATE NODE TABLE IF NOT EXISTS User(
                    id STRING,
                    name STRING,
                    created_at TIMESTAMP,
                    PRIMARY KEY (id)
                )
            """)
            
            # Create Document node table
            self._execute_safe("""
                CREATE NODE TABLE IF NOT EXISTS Document(
                    hash STRING,
                    title STRING,
                    source_path STRING,
                    source_type STRING,
                    created_at TIMESTAMP,
                    size_bytes INT64,
                    PRIMARY KEY (hash)
                )
            """)
            
            # Create Concept node table
            self._execute_safe("""
                CREATE NODE TABLE IF NOT EXISTS Concept(
                    name STRING,
                    category STRING,
                    embedding DOUBLE[384],
                    global_frequency INT64,
                    is_broad BOOLEAN,
                    first_seen TIMESTAMP,
                    PRIMARY KEY (name)
                )
            """)
            
            # Create RELATED_TO relationship table (Concept to Concept)
            self._execute_safe("""
                CREATE REL TABLE IF NOT EXISTS RELATED_TO(
                    FROM Concept TO Concept,
                    base_weight DOUBLE,
                    current_weight DOUBLE,
                    sample_size INT64,
                    confidence DOUBLE,
                    observation_variance DOUBLE,
                    last_accessed TIMESTAMP,
                    decay_rate DOUBLE
                )
            """)
            
            # Create DISCUSSES relationship table (Document to Concept)
            self._execute_safe("""
                CREATE REL TABLE IF NOT EXISTS DISCUSSES(
                    FROM Document TO Concept,
                    strength DOUBLE
                )
            """)
            
            logger.info("Schema created/verified successfully")
            
        except Exception as e:
            logger.error(f"Failed to create schema: {e}")
            raise RuntimeError(f"Schema creation failed: {e}") from e
    
    def _execute_safe(self, query: str) -> None:
        """
        Execute a query safely, catching expected errors.
        
        Args:
            query: Cypher query to execute
        """
        try:
            self.conn.execute(query)
        except Exception as e:
            # Log but don't raise for "already exists" type errors
            logger.debug(f"Query execution note: {e}")
    
    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a Cypher query and return results as DataFrame.
        
        Args:
            query: Cypher query to execute
            params: Optional query parameters
            
        Returns:
            Query results as pandas DataFrame
            
        Raises:
            RuntimeError: If query execution fails
        """
        try:
            if params:
                result = self.conn.execute(query, params)
            else:
                result = self.conn.execute(query)
            
            # Convert to DataFrame
            df = result.get_as_df()
            logger.debug(f"Query executed successfully, returned {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}\nQuery: {query}")
            raise RuntimeError(f"Query execution failed: {e}") from e
    
    def create_concept(
        self, 
        name: str, 
        embedding: List[float], 
        category: str = 'general'
    ) -> None:
        """
        Create a new concept node.
        
        Args:
            name: Concept name (primary key)
            embedding: 384-dimensional embedding vector
            category: Concept category (default: 'general')
            
        Raises:
            ValueError: If embedding dimension is not 384
            RuntimeError: If concept creation fails
        """
        if len(embedding) != 384:
            raise ValueError(f"Embedding must be 384-dimensional, got {len(embedding)}")
        
        try:
            query = """
                CREATE (c:Concept {
                    name: $name,
                    category: $category,
                    embedding: $embedding,
                    global_frequency: 1,
                    is_broad: false,
                    first_seen: $timestamp
                })
            """
            
            self.conn.execute(query, {
                'name': name,
                'category': category,
                'embedding': embedding,
                'timestamp': datetime.now()
            })
            
            logger.info(f"Created concept: {name} ({category})")
            
        except Exception as e:
            logger.error(f"Failed to create concept '{name}': {e}")
            raise RuntimeError(f"Concept creation failed: {e}") from e
    
    def get_concept(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a concept by name.
        
        Args:
            name: Concept name
            
        Returns:
            Concept data as dictionary, or None if not found
        """
        try:
            query = "MATCH (c:Concept {name: $name}) RETURN c"
            result = self.conn.execute(query, {'name': name})
            df = result.get_as_df()
            
            if df.empty:
                return None
            
            # Extract concept data from the result
            concept = df.iloc[0]['c']
            return concept
            
        except Exception as e:
            logger.error(f"Failed to retrieve concept '{name}': {e}")
            return None
    
    def create_edge(self, concept_a: str, concept_b: str, weight: float) -> None:
        """
        Create a RELATED_TO edge between two concepts.
        
        Args:
            concept_a: Source concept name
            concept_b: Target concept name
            weight: Relationship weight (0.0 to 1.0)
            
        Raises:
            ValueError: If weight is not between 0 and 1
            RuntimeError: If edge creation fails
        """
        if not 0.0 <= weight <= 1.0:
            raise ValueError(f"Weight must be between 0 and 1, got {weight}")
        
        try:
            query = """
                MATCH (a:Concept {name: $concept_a}), (b:Concept {name: $concept_b})
                CREATE (a)-[:RELATED_TO {
                    base_weight: $weight,
                    current_weight: $weight,
                    sample_size: 1,
                    confidence: 0.5,
                    observation_variance: 0.0,
                    last_accessed: $timestamp,
                    decay_rate: 0.01
                }]->(b)
            """
            
            self.conn.execute(query, {
                'concept_a': concept_a,
                'concept_b': concept_b,
                'weight': weight,
                'timestamp': datetime.now()
            })
            
            logger.info(f"Created edge: {concept_a} -> {concept_b} (weight: {weight})")
            
        except Exception as e:
            logger.error(f"Failed to create edge {concept_a} -> {concept_b}: {e}")
            raise RuntimeError(f"Edge creation failed: {e}") from e
    
    def get_node_count(self) -> int:
        """
        Get total count of all nodes in the graph.
        
        Returns:
            Total number of nodes
        """
        try:
            query = "MATCH (n) RETURN count(n) as count"
            result = self.conn.execute(query)
            df = result.get_as_df()
            return int(df.iloc[0]['count'])
            
        except Exception as e:
            logger.error(f"Failed to get node count: {e}")
            return 0
    
    def get_edge_count(self) -> int:
        """
        Get total count of all relationships in the graph.
        
        Returns:
            Total number of relationships
        """
        try:
            query = "MATCH ()-[r]->() RETURN count(r) as count"
            result = self.conn.execute(query)
            df = result.get_as_df()
            return int(df.iloc[0]['count'])
            
        except Exception as e:
            logger.error(f"Failed to get edge count: {e}")
            return 0
    
    def close(self) -> None:
        """
        Close the database connection.
        """
        try:
            # KùzuDB automatically manages connections
            # Just log the closure
            logger.info(f"Closed connection to KùzuDB at {self.db_path}")
            
        except Exception as e:
            logger.warning(f"Error during connection closure: {e}")
