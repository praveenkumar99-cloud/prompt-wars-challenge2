"""Download endpoint for generated submittals"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from .upload import job_store

router = APIRouter(prefix="/api", tags=["download"])

@router.get("/download/{job_id}")
async def download_submittal(job_id: str):
    """Download the generated submittal ZIP file"""
    job = job_store.get(job_id)
    
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")
    
    if job["status"] != "completed":
        raise HTTPException(400, f"Job {job_id} is not ready for download. Status: {job['status']}")
    
    zip_path = job.get("zip_path")
    if not zip_path or not os.path.exists(zip_path):
        raise HTTPException(404, f"Submittal file for job {job_id} not found")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"submittal_{job_id}.zip"
    )
