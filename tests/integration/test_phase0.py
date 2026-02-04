import pytest
import time
import shutil
from pathlib import Path
from queue import Queue, Empty
from mind_q_agent.watcher.file_watcher import FileWatcher

class TestPhase0Integration:
    """Integration tests for Phase 0 foundation components."""
    
    @pytest.fixture
    def watch_dir(self, tmp_path):
        """Create a temporary directory for watching."""
        d = tmp_path / "watch_data"
        d.mkdir()
        return d
        
    @pytest.fixture
    def event_queue(self):
        """Queue for receiving events."""
        return Queue()
        
    def test_watcher_queue_integration(self, watch_dir, event_queue):
        """Verify that file events are correctly queued and can be consumed."""
        # 1. Setup FileWatcher monitoring temp directory
        watcher = FileWatcher(
            watch_folder=str(watch_dir),
            queue=event_queue,
            debounce_window=0.1
        )
        
        watcher.start()
        try:
            # Allow watcher to start
            time.sleep(0.5)
            
            # 2. Create a file in that directory
            test_file = watch_dir / "test_doc.txt"
            test_file.write_text("Test content for integration")
            
            # 3. Assert that an event appears in the event_queue
            # We wait up to 2 seconds for the event (accounting for debounce/polling)
            try:
                event = event_queue.get(timeout=2.0)
            except Empty:
                pytest.fail("Timed out waiting for file event in queue")
                
            # 4. Assert event contains correct path and type
            assert event.get('type') == 'file_created' or event.get('type') == 'file_modified' or event.get('event_type') == 'created'
            assert event.get('filepath') == str(test_file)
            assert event.get('text') == "Test content for integration"
            
        finally:
            watcher.stop()
            
    def test_watcher_multiple_files(self, watch_dir, event_queue):
        """Verify handling of multiple files."""
        watcher = FileWatcher(
            watch_folder=str(watch_dir),
            queue=event_queue,
            debounce_window=0.1
        )
        
        watcher.start()
        try:
            time.sleep(0.5)
            
            # Create first file
            file1 = watch_dir / "doc1.txt"
            file1.write_text("Content 1")
            
            # Create second file
            file2 = watch_dir / "doc2.md"
            file2.write_text("# Content 2")
            
            # Collect events
            events = []
            start_time = time.time()
            while len(events) < 2 and time.time() - start_time < 3.0:
                try:
                    events.append(event_queue.get(timeout=0.5))
                except Empty:
                    continue
            
            assert len(events) == 2, f"Expected 2 events, got {len(events)}"
            paths = {e['filepath'] for e in events}
            assert str(file1) in paths
            assert str(file2) in paths
            
        finally:
            watcher.stop()
