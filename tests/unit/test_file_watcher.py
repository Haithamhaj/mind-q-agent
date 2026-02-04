"""
Unit tests for File Watcher module.
"""

import threading
import time
from queue import Queue
from pathlib import Path

import pytest
from mind_q_agent.watcher.file_watcher import FileWatcher


class TestFileWatcher:
    
    @pytest.fixture
    def watcher_setup(self, tmp_path):
        """Setup watcher and queue for testing."""
        queue = Queue()
        watcher = FileWatcher(str(tmp_path), queue, debounce_window=0.1)
        return watcher, queue, tmp_path

    def test_watcher_creation(self, watcher_setup):
        """Test initialization creates directory and sets attributes."""
        watcher, queue, path = watcher_setup
        assert watcher.watch_folder == path
        assert watcher.queue == queue
        assert path.exists()

    def test_detect_new_txt(self, watcher_setup):
        """Test detecting and processing a new text file."""
        watcher, queue, path = watcher_setup
        
        # Create file
        test_file = path / "test.txt"
        content = "Hello Watcher"
        test_file.write_text(content, encoding='utf-8')
        
        # Process manually (to avoid relying on thread timing in unit test)
        result = watcher.process_file(str(test_file), "created")
        
        assert result is not None
        assert result['filename'] == "test.txt"
        assert result['text'] == content
        assert result['file_type'] == ".txt"
        assert not queue.empty()

    def test_ignore_unsupported(self, watcher_setup):
        """Test ignoring unsupported file extensions."""
        watcher, queue, path = watcher_setup
        
        test_file = path / "image.png"
        test_file.write_bytes(b"fake image")
        
        result = watcher.process_file(str(test_file), "created")
        
        assert result is None
        assert queue.empty()
        
    def test_debouncing(self, watcher_setup):
        """Test that rapid events are debounced."""
        watcher, queue, path = watcher_setup
        watcher.debounce_window = 1.0
        
        test_file = path / "debounce.md"
        test_file.write_text("# Test", encoding='utf-8')
        
        # First process: Should succeed
        res1 = watcher.process_file(str(test_file), "modified")
        assert res1 is not None
        
        # Second process immediately: Should be skipped
        res2 = watcher.process_file(str(test_file), "modified")
        assert res2 is None
        
    def test_file_hash_consistency(self, watcher_setup):
        """Test that same content produces same hash."""
        watcher, queue, path = watcher_setup
        
        content = "Consistent Content"
        
        file1 = path / "file1.txt"
        file1.write_text(content)
        
        file2 = path / "file2.txt"
        file2.write_text(content)
        
        res1 = watcher.process_file(str(file1))
        res2 = watcher.process_file(str(file2))
        
        assert res1['file_hash'] == res2['file_hash']
        assert res1['filepath'] != res2['filepath']

    def test_integration_threading(self, watcher_setup):
        """Integration test with actual background thread."""
        watcher, queue, path = watcher_setup
        
        watcher.start()
        time.sleep(1)  # Let it start
        
        try:
            # Create file
            f = path / "realOps.txt"
            f.write_text("Real operation")
            
            # Wait for detection
            time.sleep(2)
            
            assert not queue.empty()
            item = queue.get()
            assert item['filename'] == "realOps.txt"
            
        finally:
            watcher.stop()
