
import requests
import sys
import os
import zipfile
import shutil

# Config
PORT = 8778
BASE_URL = f"http://127.0.0.1:{PORT}/api/v1/system"
BACKUP_DIR = "backups"

def run_tests():
    print(f"Running tests against {BASE_URL}...")
    
    # 1. Trigger Backup
    backup_file = "test_backup.zip"
    try:
        r = requests.get(f"{BASE_URL}/backup", stream=True)
        assert r.status_code == 200
        
        with open(backup_file, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                
        if zipfile.is_zipfile(backup_file):
            print(f"[PASS] Create Backup ({os.path.getsize(backup_file)} bytes)")
        else:
            print("[FAIL] Backup file is not a valid zip")
            return False
            
    except Exception as e:
        print(f"[FAIL] Create Backup: {e}")
        return False

    # 2. Restore Backup
    # We'll use the backup we just created
    try:
        with open(backup_file, "rb") as f:
            files = {"file": (backup_file, f, "application/zip")}
            r = requests.post(f"{BASE_URL}/restore", files=files)
            
        if r.status_code == 200:
             print("[PASS] Restore Backup")
        else:
             print(f"[FAIL] Restore Backup: {r.status_code} {r.text}")
             return False
    except Exception as e:
        print(f"[FAIL] Restore Backup: {e}")
        return False
    finally:
        if os.path.exists(backup_file):
            os.remove(backup_file)

    return True

if __name__ == "__main__":
    if run_tests():
        print("\n✅ System Verification SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ System Verification FAILED")
        sys.exit(1)
