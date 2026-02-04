from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
import logging
import shutil
import os
import zipfile
from datetime import datetime
from pathlib import Path

router = APIRouter(
    prefix="/system",
    tags=["system"]
)

logger = logging.getLogger(__name__)

DATA_DIR = Path("data")
BACKUP_DIR = Path("backups")

# Ensure backup dir exists
os.makedirs(BACKUP_DIR, exist_ok=True)

@router.get("/backup", response_class=FileResponse)
def create_backup(background_tasks: BackgroundTasks):
    """
    Create a backup of the data directory and return it as a ZIP file.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"mind_q_backup_{timestamp}.zip"
        backup_path = BACKUP_DIR / backup_filename
        
        # Zip the data directory
        shutil.make_archive(str(backup_path.with_suffix('')), 'zip', DATA_DIR)
        
        # Cleanup after sending (using background task)
        # background_tasks.add_task(os.remove, backup_path) # Optional: keep backups or delete
        
        return FileResponse(
            path=str(backup_path), 
            filename=backup_filename, 
            media_type='application/zip'
        )
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore")
async def restore_backup(file: UploadFile = File(...)):
    """
    Restore system data from a backup ZIP file.
    WARNING: This will overwrite existing data.
    """
    try:
        # Save uploaded file temporarily
        temp_zip_path = BACKUP_DIR / f"restore_{datetime.now().timestamp()}.zip"
        with open(temp_zip_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        # Verify zip
        if not zipfile.is_zipfile(temp_zip_path):
            raise HTTPException(status_code=400, detail="Invalid ZIP file")
            
        # Extract
        # CAUTION: This overwrites files in DATA_DIR.
        # Ideally we should stop services/DBs here.
        # For now, we assume "at own risk" or idle state.
        
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
            
        # Cleanup
        os.remove(temp_zip_path)
            
        return {"message": "System restored successfully. Please restart if necessary."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
