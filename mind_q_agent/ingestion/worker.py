import logging
import threading
from queue import Queue
from pathlib import Path
from typing import Dict, Any

from mind_q_agent.ingestion.pipeline import IngestionPipeline

logger = logging.getLogger(__name__)

class IngestionWorker(threading.Thread):
    """
    Background worker thread that consumes file events from the queue
    and processes them using the IngestionPipeline.
    """
    
    def __init__(self, event_queue: Queue, pipeline: IngestionPipeline):
        """
        Initialize the worker.
        
        Args:
            event_queue: Queue containing file events (dicts)
            pipeline: Initialized IngestionPipeline instance
        """
        super().__init__(name="IngestionWorker", daemon=True)
        self.event_queue = event_queue
        self.pipeline = pipeline
        self._stop_event = threading.Event()

    def run(self):
        """
        Main worker loop. 
        Consumes items until "STOP" sentinel or stop event is set.
        """
        logger.info("IngestionWorker started.")
        
        while not self._stop_event.is_set():
            try:
                # Get item with timeout to allow checking stop_event periodically
                try:
                    item = self.event_queue.get(timeout=1.0)
                except Exception:
                    # Queue empty, verify stop condition
                    continue

                if item == "STOP":
                    logger.info("Received STOP signal. Shutting down worker.")
                    self.event_queue.task_done()
                    break
                
                # Should be a dict from FileWatcher
                if not isinstance(item, dict):
                    logger.warning(f"Invalid item in queue: {item}")
                    self.event_queue.task_done()
                    continue

                self._process_item(item)
                
                # Mark task done
                self.event_queue.task_done()
                
            except Exception as e:
                # Critical catch-all to prevent thread death
                logger.error(f"Critical worker error: {e}", exc_info=True)

        logger.info("IngestionWorker stopped.")

    def _process_item(self, item: Dict[str, Any]):
        """Helper to process a single queue item."""
        try:
            filepath_str = item.get("filepath")
            text = item.get("text")
            
            if not filepath_str or not text:
                logger.warning(f"Incomplete event data: {item.keys()}")
                return

            path = Path(filepath_str)
            logger.debug(f"Worker picking up: {path.name}")
            
            # Delegate to pipeline
            self.pipeline.process_document(path, text)
            
        except Exception as e:
            logger.error(f"Error processing item {item.get('filename')}: {e}")

    def stop(self):
        """Signal the worker to stop."""
        self._stop_event.set()
