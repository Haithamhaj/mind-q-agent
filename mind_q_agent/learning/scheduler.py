import logging
import threading
import time
from typing import Optional, Callable, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MaintenanceScheduler:
    """
    Simple scheduler to run maintenance jobs periodically.
    
    Jobs include:
    - Hebbian Update Cycle
    - Decay Batch Job
    - Prune Job
    """
    
    def __init__(self):
        self._jobs: List[dict] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_job(self, name: str, job_fn: Callable[[], int], interval_hours: float):
        """
        Register a job to run periodically.
        
        Args:
            name: Job name for logging.
            job_fn: Callable that returns count of items processed.
            interval_hours: How often to run (in hours).
        """
        self._jobs.append({
            "name": name,
            "fn": job_fn,
            "interval": timedelta(hours=interval_hours),
            "last_run": None
        })
        logger.info(f"Registered job: {name} (every {interval_hours}h)")

    def start(self):
        """Start the scheduler in a background thread."""
        if self._running:
            logger.warning("Scheduler already running.")
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="MaintenanceScheduler")
        self._thread.start()
        logger.info("Maintenance scheduler started.")

    def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("Maintenance scheduler stopped.")

    def _run_loop(self):
        """Main scheduler loop."""
        while self._running:
            now = datetime.now()
            
            for job in self._jobs:
                # Check if job should run
                if job["last_run"] is None or (now - job["last_run"]) >= job["interval"]:
                    try:
                        logger.info(f"Running job: {job['name']}")
                        result = job["fn"]()
                        job["last_run"] = now
                        logger.info(f"Job {job['name']} completed: {result} items processed.")
                    except Exception as e:
                        logger.error(f"Job {job['name']} failed: {e}", exc_info=True)
            
            # Sleep for 1 minute between checks
            time.sleep(60)

    def run_all_now(self):
        """Manually trigger all jobs immediately (for testing/CLI)."""
        results = {}
        for job in self._jobs:
            try:
                logger.info(f"Running job: {job['name']}")
                result = job["fn"]()
                job["last_run"] = datetime.now()
                results[job["name"]] = result
            except Exception as e:
                logger.error(f"Job {job['name']} failed: {e}")
                results[job["name"]] = -1
        return results
