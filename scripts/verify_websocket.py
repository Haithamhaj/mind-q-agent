
import asyncio
import websockets
import json
import requests
import sys

# Config
PORT = 8774
WS_URL = f"ws://127.0.0.1:{PORT}/api/v1/ws/events"
UPLOAD_URL = f"http://127.0.0.1:{PORT}/api/v1/documents/upload"
TEST_FILENAME = "test_ws_event.txt"

async def listen_for_events():
    async with websockets.connect(WS_URL) as websocket:
        print(f"[WS] Connected to {WS_URL}")
        
        while True:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                data = json.loads(message)
                print(f"[WS] Received event: {data['type']}")
                
                if data['type'] == "ingestion_started":
                    print("[PASS] Received ingestion_started")
                elif data['type'] == "ingestion_completed":
                    print("[PASS] Received ingestion_completed")
                    return True # Success
                elif data['type'] == "ingestion_failed":
                    print(f"[FAIL] Received ingestion_failed: {data}")
                    return False
                    
            except asyncio.TimeoutError:
                print("[FAIL] Timeout waiting for event")
                return False

def trigger_upload():
    print(f"[HTTP] Uploading {TEST_FILENAME}...")
    with open(TEST_FILENAME, "w") as f:
        f.write("Test WebSocket Event Trigger")
        
    with open(TEST_FILENAME, "rb") as f:
        files = {"file": (TEST_FILENAME, f, "text/plain")}
        requests.post(UPLOAD_URL, files=files)
    
    import os
    if os.path.exists(TEST_FILENAME):
        os.remove(TEST_FILENAME)

async def main():
    # Start listener and trigger in parallel
    listener = asyncio.create_task(listen_for_events())
    
    # Wait a bit for connection
    await asyncio.sleep(2)
    trigger_upload()
    
    success = await listener
    if success:
        print("\n✅ WebSocket Verification SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ WebSocket Verification FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
