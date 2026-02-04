import argparse
import shutil
import sys
from pathlib import Path

# Add project root to python path to allow imports
base_dir = Path(__file__).parent.parent
sys.path.append(str(base_dir))

from mind_q_agent.config.manager import ConfigManager
from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.utils.logger import setup_logging
import logging

def main():
    parser = argparse.ArgumentParser(description="Initialize Mind-Q Databases")
    parser.add_argument("--reset", action="store_true", help="Delete existing database before initializing")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen without doing it")
    args = parser.parse_args()
    
    setup_logging()
    config = ConfigManager.get_config()
    db_path = config["db"]["graph_path"]
    
    if args.reset:
        if args.dry_run:
            logging.info(f"[DRY RUN] Would delete directory: {db_path}")
        else:
            if Path(db_path).exists():
                logging.warning(f"Deleting existing database at {db_path}...")
                shutil.rmtree(db_path)
                logging.info("Deleted.")
            else:
                logging.info("No existing database to delete.")

    if args.dry_run:
        logging.info(f"[DRY RUN] Would initialize KùzuDB at: {db_path}")
        return

    # Initialize Graph DB (this creates folders and schema)
    logging.info(f"Initializing KùzuDB at {db_path}...")
    try:
        graph = KuzuGraphDB(db_path)
        # Assuming KuzuGraphDB.__init__ calls initialize_schema() internally
        # If not, verify if we need to call it explicitly. 
        # Checking previous implementation... yes it calls _initialize_schema
        logging.info("✅ Database initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
