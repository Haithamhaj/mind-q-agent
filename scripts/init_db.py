#!/usr/bin/env python3
"""
Mind-Q Agent Database Initialization Script

This script initializes/migrates the database schema for:
1. KùzuDB Graph Database
2. ChromaDB Vector Database  
3. SQLite Interaction Database

Usage:
    python scripts/init_db.py [--reset]
    
Options:
    --reset  Reset all databases (WARNING: deletes all data)
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mind_q_agent.config.manager import ConfigManager
from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.vector.chroma_vector import ChromaVectorDB
from mind_q_agent.learning.tracker import InteractionTracker

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def init_graph_db(reset: bool = False) -> bool:
    """Initialize KùzuDB graph database."""
    try:
        config = ConfigManager.get_config()
        db_path = config.get("db", {}).get("graph_path", "./data/graph_db")
        
        if reset:
            import shutil
            path = Path(db_path)
            if path.exists():
                shutil.rmtree(path)
                logger.info(f"Reset graph database at {db_path}")
        
        # Initialize graph - this creates schema automatically
        graph = KuzuGraphDB(db_path=db_path)
        logger.info(f"✅ Graph database initialized at {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize graph database: {e}")
        return False


def init_vector_db(reset: bool = False) -> bool:
    """Initialize ChromaDB vector database."""
    try:
        config = ConfigManager.get_config()
        db_path = config.get("db", {}).get("vector_path", "./data/vector_db")
        
        if reset:
            import shutil
            path = Path(db_path)
            if path.exists():
                shutil.rmtree(path)
                logger.info(f"Reset vector database at {db_path}")
        
        # Initialize vector DB
        vector_db = ChromaVectorDB(db_path=db_path)
        logger.info(f"✅ Vector database initialized at {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize vector database: {e}")
        return False


def init_interaction_db(reset: bool = False) -> bool:
    """Initialize SQLite interaction database."""
    try:
        db_path = "./data/interactions.db"
        
        if reset:
            path = Path(db_path)
            if path.exists():
                path.unlink()
                logger.info(f"Reset interaction database at {db_path}")
        
        # Initialize tracker - this creates schema automatically
        tracker = InteractionTracker(db_path=db_path)
        logger.info(f"✅ Interaction database initialized at {db_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize interaction database: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Initialize Mind-Q databases")
    parser.add_argument("--reset", action="store_true", help="Reset all databases")
    args = parser.parse_args()
    
    if args.reset:
        logger.warning("⚠️  RESET mode: All existing data will be deleted!")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            logger.info("Cancelled.")
            return
    
    print("\n" + "=" * 50)
    print("   MIND-Q AGENT DATABASE INITIALIZATION")
    print("=" * 50 + "\n")
    
    results = {
        "Graph DB": init_graph_db(args.reset),
        "Vector DB": init_vector_db(args.reset),
        "Interaction DB": init_interaction_db(args.reset),
    }
    
    print("\n" + "-" * 50)
    print("SUMMARY:")
    for db, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {db}: {status}")
    
    all_success = all(results.values())
    print("-" * 50)
    
    if all_success:
        print("✅ All databases initialized successfully!")
    else:
        print("❌ Some databases failed to initialize.")
        sys.exit(1)


if __name__ == "__main__":
    main()
