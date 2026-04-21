"""Job status endpoint"""
from fastapi import APIRouter, HTTPException
from ..db import get_job
from ..models import JobResponse, JobStatus

router = APIRouter(prefix="/api", tags=["status"])

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get the status of a processing job"""
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")
    
    return {
        "job_id": job_id,
        "status": job.get("status"),
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at", job.get("created_at")),
        "total_parts": job.get("total_parts"),
        "missing_parts": job.get("missing_parts"),
        "error_message": job.get("error_message")
    }
