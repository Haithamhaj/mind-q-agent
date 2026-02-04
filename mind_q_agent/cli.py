import argparse
import sys
import logging
from pathlib import Path
from queue import Queue
import time

from mind_q_agent.config.manager import ConfigManager
from mind_q_agent.utils.logger import setup_logging
from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.vector.chroma_vector import ChromaVectorDB
from mind_q_agent.ingestion.pipeline import IngestionPipeline
from mind_q_agent.ingestion.worker import IngestionWorker
from mind_q_agent.watcher.file_watcher import FileWatcher
from mind_q_agent.search.engine import SearchEngine

logger = logging.getLogger(__name__)

class MindQCli:
    """Command Line Interface for Mind-Q Agent."""

    def __init__(self):
        self.config = ConfigManager()
        setup_logging(log_file="mind_q.log")
        self._init_components()

    def _init_components(self):
        """Initialize all core components."""
        try:
            logger.info("Initializing Mind-Q components...")
            # ConfigManager.get(section, key)
            db_path = self.config.get("db", "graph_path")
            vector_path = self.config.get("db", "vector_path")
            # Collection name not in default.yaml, provide fallback
            vector_collection = self.config.get("db", "vector_collection", "mind_q_collection")
            
            self.graph_db = KuzuGraphDB(db_path=db_path)
            self.vector_store = ChromaVectorDB(
                db_path=vector_path,
                collection_name=vector_collection
            )
            self.pipeline = IngestionPipeline(self.graph_db, self.vector_store)
            self.search_engine = SearchEngine(self.vector_store)
            logger.info("Components initialized.")
        except Exception as e:
            logger.critical(f"Failed to initialize components: {e}")
            sys.exit(1)

    def run(self):
        """Parse args and execute command."""
        parser = argparse.ArgumentParser(description="Mind-Q Agent CLI")
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Command: ingest
        ingest_parser = subparsers.add_parser("ingest", help="Batch ingest documents from directory")
        ingest_parser.add_argument("--dir", required=True, help="Directory path to scan")

        # Command: search
        search_parser = subparsers.add_parser("search", help="Semantic search")
        search_parser.add_argument("query", help="Search query string")
        search_parser.add_argument("--limit", type=int, default=5, help="Number of results")

        # Command: watch
        watch_parser = subparsers.add_parser("watch", help="Start background file watcher daemon")
        watch_parser.add_argument("--dir", required=True, help="Directory path to watch")

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        if args.command == "ingest":
            self.ingest(args.dir)
        elif args.command == "search":
            self.search(args.query, args.limit)
        elif args.command == "watch":
            self.watch(args.dir)

    def ingest(self, dir_path: str):
        """Ingest all supported files in a directory."""
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            logger.error(f"Invalid directory: {dir_path}")
            return

        logger.info(f"Scanning directory: {path}")
        count = 0
        for file_path in path.glob("*"):
            if file_path.suffix in ['.txt', '.md', '.pdf']:
                try:
                    # Simple text read for now, ideally reuse FileWatcher logic or extract logic
                    # For consistency, let's just read text here or instantiate a watcher to scan once?
                    # Let's read text directly here for simplicity of 'batch ingest'
                    if file_path.suffix == '.pdf':
                        import fitz
                        doc = fitz.open(file_path)
                        text = "".join([page.get_text() for page in doc])
                    else:
                        text = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    if text.strip():
                        if self.pipeline.process_document(file_path, text):
                            count += 1
                except Exception as e:
                    logger.error(f"Failed to ingest {file_path}: {e}")
        
        logger.info(f"Batch ingestion complete. Processed {count} documents.")

    def search(self, query: str, limit: int):
        """Execute search and print results."""
        logger.info(f"Searching for: '{query}'")
        results = self.search_engine.search(query, limit)
        
        if not results:
            print("No results found.")
            return

        print(f"\nFound {len(results)} results:\n" + "="*40)
        for i, res in enumerate(results, 1):
            print(f"{i}. [Score: {res['score']:.4f}] {res['id']}")
            print(f"   Source: {res['metadata'].get('source', 'Unknown')}")
            snippet = res['text'][:200].replace('\n', ' ') + "..."
            print(f"   Text: {snippet}\n")
            
    def watch(self, dir_path: str):
        """Start daemon mode."""
        event_queue = Queue()
        
        # Start Worker
        worker = IngestionWorker(event_queue, self.pipeline)
        worker.start()
        
        # Start Watcher
        watcher = FileWatcher(dir_path, event_queue)
        watcher.start()
        
        logger.info(f"Mind-Q Daemon started. Watching: {dir_path}")
        logger.info("Press Ctrl+C to stop.")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\nStopping daemon...")
            watcher.stop()
            event_queue.put("STOP")
            worker.join()
            logger.info("Daemon stopped.")
