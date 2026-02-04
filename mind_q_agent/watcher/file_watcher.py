"""
File Watcher module for monitoring file system changes.

This module provides the FileWatcher class which uses watchdog to monitor
directories for new or modified files and queues them for processing.
"""

import hashlib
import logging
import time
from pathlib import Path
from queue import Queue
from typing import Any, Dict, Optional

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

# Optional PyMuPDF import
try:
    import fitz
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

logger = logging.getLogger(__name__)


class MindQFileHandler(FileSystemEventHandler):
    """
    Handles file system events and triggers processing.
    """
    
    def __init__(self, watcher: 'FileWatcher'):
        self.watcher = watcher
        
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if event.is_directory:
            return
        self.watcher.process_file(event.src_path, event_type="created")
        
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if event.is_directory:
            return
        self.watcher.process_file(event.src_path, event_type="modified")


class FileWatcher:
    """
    Monitors a directory for file changes and processes supported files.
    
    Attributes:
        watch_folder: Path to the folder to watch
        queue: Queue to put processed file data into
        debounce_window: Time in seconds to ignore duplicate events
    """
    
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.pdf'}
    
    def __init__(
        self, 
        watch_folder: str, 
        queue: Queue, 
        debounce_window: float = 1.0
    ):
        """
        Initialize the FileWatcher.
        
        Args:
            watch_folder: Directory to watch
            queue: Queue for processed data
            debounce_window: Seconds to wait before re-processing same file
        """
        self.watch_folder = Path(watch_folder)
        self.queue = queue
        self.debounce_window = debounce_window
        
        self.observer = Observer()
        self.event_handler = MindQFileHandler(self)
        self._last_processed: Dict[str, float] = {}
        
        # Create watch folder if needed
        self.watch_folder.mkdir(parents=True, exist_ok=True)

    def start(self) -> None:
        """Start the file watcher in a background thread."""
        self.observer.schedule(
            self.event_handler, 
            str(self.watch_folder), 
            recursive=True
        )
        self.observer.start()
        logger.info(f"Started watching: {self.watch_folder}")

    def stop(self) -> None:
        """Stop the file watcher."""
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped file watcher")

    def process_file(self, filepath: str, event_type: str = "detected") -> Optional[Dict[str, Any]]:
        """
        Process a file: extract text and metadata.
        
        Args:
            filepath: Path to the file
            event_type: Type of event (created, modified, detected)
            
        Returns:
            Dict containing file data or None if skipped
        """
        path = Path(filepath)
        
        # 1. Filter by extension
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return None
            
        # 2. Debouncing
        current_time = time.time()
        last_time = self._last_processed.get(filepath, 0)
        
        if (current_time - last_time) < self.debounce_window:
            logger.debug(f"Debounced: {path.name}")
            return None
            
        self._last_processed[filepath] = current_time
        
        try:
            # 3. Extract text
            text = self._extract_text(path)
            if not text:
                logger.warning(f"No text extracted from {path.name}")
                return None
                
            # 4. Calculate hash
            file_hash = self._calculate_hash(text)
            
            # 5. Prepare data
            stat = path.stat()
            file_data = {
                "filepath": str(path),
                "filename": path.name,
                "file_hash": file_hash,
                "text": text,
                "size_bytes": stat.st_size,
                "modified_at": stat.st_mtime,
                "file_type": path.suffix.lower(),
                "event_type": event_type
            }
            
            # 6. Add to queue
            self.queue.put(file_data)
            logger.info(f"Processed file: {path.name} ({event_type})")
            return file_data
            
        except Exception as e:
            logger.error(f"Error processing {path.name}: {e}")
            return None

    def _extract_text(self, path: Path) -> Optional[str]:
        """Extract text content based on file type."""
        ext = path.suffix.lower()
        
        try:
            if ext in {'.txt', '.md'}:
                return path.read_text(encoding='utf-8')
                
            elif ext == '.pdf':
                if not HAS_PYMUPDF:
                    logger.warning("PyMuPDF not installed, skipping PDF")
                    return None
                    
                text = ""
                with fitz.open(path) as doc:
                    for page in doc:
                        text += page.get_text()
                return text
                
        except UnicodeDecodeError:
            logger.warning(f"Encoding error reading {path.name}")
        except Exception as e:
            logger.error(f"Extraction failed for {path.name}: {e}")
            
        return None

    def _calculate_hash(self, text: str) -> str:
        """Calculate SHA-256 hash of text content."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
