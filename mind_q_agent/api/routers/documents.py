from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import shutil
import os
from pathlib import Path
import logging

from mind_q_agent.ingestion.pipeline import IngestionPipeline
from mind_q_agent.ingestion.file_parser import FileParser
from mind_q_agent.graph.kuzu_graph import KuzuGraphDB
from mind_q_agent.vector.chroma_vector import ChromaVectorDB
from mind_q_agent.api.settings import settings

router = APIRouter(
    prefix="/documents",
    tags=["documents"]
)

logger = logging.getLogger(__name__)

# Initialize singletons for DBs (Poor man's dependency injection for now)
# In a real prod app, use FastAPI Depends
try:
    graph_db = KuzuGraphDB(settings.KUZU_DB_PATH)
    vector_db = ChromaVectorDB(settings.CHROMA_DB_PATH)
    pipeline = IngestionPipeline(graph_db, vector_db)
except Exception as e:
    logger.error(f"Failed to initialize DBs: {e}")
    # We allow app to start, but endpoints might fail. 
    # Better to fail fast, but for dev we continue.
    graph_db = None
    pipeline = None

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a document (PDF, MD, TXT), parse it, and ingest it.
    """
    if not pipeline:
        raise HTTPException(status_code=500, detail="Ingestion pipeline not initialized")

    try:
        # 1. Parse content immediately to get text
        text = await FileParser.parse_file(file)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="File is empty or could not be parsed")

        # 2. Save file temporarily (optional, but good for record/hashing consistency)
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / (file.filename or "untitled")
        
        # Write bytes
        with open(file_path, "wb") as f:
            await file.seek(0)
            shutil.copyfileobj(file.file, f)
            
        # 3. Trigger Ingestion (Synchronous for now to return result, could be background)
        # We'll do it synchronously to give immediate feedback for this phase
        success = pipeline.process_document(file_path.absolute(), text)
        
        if not success:
             return {"message": "Document already exists (deduplicated)", "filename": file.filename}

        return {"message": "Document uploaded and ingested successfully", "filename": file.filename}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Dict[str, Any]])
def list_documents():
    """List all documents from the Graph DB."""
    if not graph_db:
         raise HTTPException(status_code=500, detail="Graph DB not initialized")
    
    query = """
        MATCH (d:Document)
        RETURN d.hash as hash, d.title as title, d.created_at as created_at, d.size_bytes as size
        ORDER BY d.created_at DESC
    """
    try:
        df = graph_db.execute(query)
        # Convert DataFrame to list of dicts
        if df.empty:
            return []
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"List documents failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{doc_hash}")
def get_document(doc_hash: str):
    """Get metadata for a specific document."""
    if not graph_db:
         raise HTTPException(status_code=500, detail="Graph DB not initialized")

    query = """
        MATCH (d:Document {hash: $hash})
        RETURN d.hash as hash, d.title as title, d.created_at as created_at, d.source_path as path
    """
    try:
        df = graph_db.execute(query, {"hash": doc_hash})
        if df.empty:
            raise HTTPException(status_code=404, detail="Document not found")
        return df.iloc[0].to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
