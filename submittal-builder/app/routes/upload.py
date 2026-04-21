"""File upload endpoint"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from ..services.orchestrator import Orchestrator
from ..utils.file_handler import FileHandler
from ..models import JobResponse, JobStatus
from datetime import datetime
from ..db import save_job

router = APIRouter(prefix="/api", tags=["upload"])
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a BOM file and start submittal generation"""
    try:
        valid_extensions = ['.pdf', '.csv', '.txt']
        file_ext = f".{file.filename.split('.')[-1].lower()}" if '.' in file.filename else ''
        
        if file_ext not in valid_extensions:
            raise HTTPException(400, f"Invalid file type. Allowed: {valid_extensions}")
        
        content = await file.read()
        file_path, job_id = FileHandler.save_upload_file(content, file.filename)
        
        initial_job = {
            "status": JobStatus.PROCESSING.value,
            "created_at": datetime.now().isoformat(),
            "file_path": file_path,
            "error_message": None,
            "zip_path": None,
            "missing_parts": None,
            "total_parts": None
        }
        save_job(job_id, initial_job)
        
        try:
            text = FileHandler.extract_text_from_file(file_path)
            orchestrator = Orchestrator()
            zip_path, missing_parts, documents_map = orchestrator.process(job_id, text)
            
            save_job(job_id, {
                "status": JobStatus.COMPLETED.value,
                "zip_path": zip_path,
                "missing_parts": missing_parts,
                "total_parts": len(documents_map),
                "updated_at": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Processing failed for job {job_id}: {e}")
            save_job(job_id, {
                "status": JobStatus.FAILED.value,
                "error_message": str(e),
                "updated_at": datetime.now().isoformat()
            })
        
        FileHandler.cleanup_temp_files(job_id)
        
        return JSONResponse(content={
            "job_id": job_id,
            "status": JobStatus.COMPLETED.value,
            "message": "Processing finished"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(500, f"Internal server error: {str(e)}")
