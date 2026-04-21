"""Download endpoint for generated submittals"""
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from ..db import get_job

router = APIRouter(prefix="/api", tags=["download"])

@router.get("/download/{job_id}")
async def download_submittal(job_id: str):
    """Download the generated submittal ZIP file"""
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(404, f"Job {job_id} not found")
    
    if job.get("status") != "completed":
        raise HTTPException(400, f"Job {job_id} is not ready for download. Status: {job.get('status')}")
    
    zip_path = job.get("zip_path")
    if not zip_path:
        raise HTTPException(404, f"Submittal file for job {job_id} not found")
        
    # If the file is physically stored in GCS, redirect to authenticated URL or generate signed URL. 
    # For simplicity, if it's gs:// we return standard storage link (assumes public output bucket)
    # or handle via explicit streaming proxy in production.
    if zip_path.startswith("gs://"):
        try:
            from google.cloud import storage
            from ..config import config
            client = storage.Client(project=config.GCP_PROJECT) if config.GCP_PROJECT else storage.Client()
            bucket_name = zip_path.split("/")[2]
            blob_name = "/".join(zip_path.split("/")[3:])
            blob = client.bucket(bucket_name).blob(blob_name)
            
            # Generate temporary download signed url (1 hour)
            import datetime
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(hours=1),
                method="GET"
            )
            return RedirectResponse(url)
        except Exception:
            raise HTTPException(500, "Error generating download link from Cloud Storage.")

    
    if not os.path.exists(zip_path):
        raise HTTPException(404, f"Local submittal file for job {job_id} not found")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"submittal_{job_id}.zip"
    )
