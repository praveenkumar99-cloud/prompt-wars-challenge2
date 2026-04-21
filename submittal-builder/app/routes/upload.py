"""File upload endpoint"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from ..services.orchestrator import Orchestrator
from ..utils.file_handler import FileHandler
from ..models import JobResponse, JobStatus
from datetime import datetime

router = APIRouter(prefix="/api", tags=["upload"])
logger = logging.getLogger(__name__)

# In-memory job store (production would use database)
job_store = {}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a BOM file and start submittal generation"""
    try:
        # Validate file extension
        valid_extensions = ['.pdf', '.csv', '.txt']
        file_ext = f".{file.filename.split('.')[-1].lower()}" if '.' in file.filename else ''
        
        if file_ext not in valid_extensions:
            raise HTTPException(400, f"Invalid file type. Allowed: {valid_extensions}")
        
        # Read and save file
        content = await file.read()
        file_path, job_id = FileHandler.save_upload_file(content, file.filename)
        
        # Create job record
        job_store[job_id] = {
            "status": JobStatus.PROCESSING,
            "created_at": datetime.now(),
            "file_path": file_path,
            "error_message": None,
            "zip_path": None,
            "missing_parts": None,
            "total_parts": None
        }
        
        # Start async processing (simplified - in production use background tasks)
        try:
            text = FileHandler.extract_text_from_file(file_path)
            orchestrator = Orchestrator()
            zip_path, missing_parts, documents_map = orchestrator.process(job_id, text)
            
            job_store[job_id]["status"] = JobStatus.COMPLETED
            job_store[job_id]["zip_path"] = zip_path
            job_store[job_id]["missing_parts"] = missing_parts
            job_store[job_id]["total_parts"] = len(documents_map)
            job_store[job_id]["updated_at"] = datetime.now()
            
        except Exception as e:
            logger.error(f"Processing failed for job {job_id}: {e}")
            job_store[job_id]["status"] = JobStatus.FAILED
            job_store[job_id]["error_message"] = str(e)
            job_store[job_id]["updated_at"] = datetime.now()
        
        # Cleanup uploaded file
        FileHandler.cleanup_temp_files(job_id)
        
        return JSONResponse(content={
            "job_id": job_id,
            "status": job_store[job_id]["status"],
            "message": "Processing completed" if job_store[job_id]["status"] == JobStatus.COMPLETED else "Processing failed"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(500, f"Internal server error: {str(e)}")
