"""
Example usage of the FileWatcher component.

This script demonstrates how to use the FileWatcher to monitor a directory
for changes and process new files in real-time.
"""

import time
import shutil
from pathlib import Path
from queue import Queue
from mind_q_agent.watcher.file_watcher import FileWatcher


def main():
    """Run the file watcher demonstration."""
    
    # Setup directories
    watch_dir = Path("./data/uploads")
    watch_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize queue and watcher
    queue = Queue()
    watcher = FileWatcher(str(watch_dir), queue, debounce_window=1.0)
    
    print(f"👀 Watching directory: {watch_dir.absolute()}")
    print("   Supported formats: .txt, .md, .pdf")
    print("   Press Ctrl+C to stop\n")
    
    try:
        watcher.start()
        
        # Simulate some activity if directory is empty
        example_file = watch_dir / "welcome.md"
        if not example_file.exists():
            print("📝 Creating example file...")
            example_file.write_text(
                "# Welcome to Mind-Q\nThis file was automatically created to test the watcher.",
                encoding='utf-8'
            )
            
        while True:
            if not queue.empty():
                file_data = queue.get()
                print("-" * 50)
                print(f"📄 Event Detected: {file_data['event_type']}")
                print(f"   File: {file_data['filename']}")
                print(f"   Type: {file_data['file_type']}")
                print(f"   Size: {file_data['size_bytes']} bytes")
                print(f"   Hash: {file_data['file_hash'][:8]}...")
                print(f"   Text Preview: {file_data['text'][:50].replace(chr(10), ' ')}...")
                print("-" * 50)
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping watcher...")
    finally:
        watcher.stop()
        print("✅ Watcher stopped.")


if __name__ == "__main__":
    main()
