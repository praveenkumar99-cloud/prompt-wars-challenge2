"""Job status endpoint"""
from fastapi import APIRouter, HTTPException
from .upload import job_store
from ..models import JobResponse, JobStatus

router = APIRouter(prefix="/api", tags=["status"])

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    """Get the status of a processing job"""
    job = job_store.get(job_id)
    
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")
    
    return {
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"].isoformat() if job["created_at"] else None,
        "updated_at": job.get("updated_at", job["created_at"]).isoformat() if job.get("updated_at") else None,
        "total_parts": job.get("total_parts"),
        "missing_parts": job.get("missing_parts"),
        "error_message": job.get("error_message")
    }
