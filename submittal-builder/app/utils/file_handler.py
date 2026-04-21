"""File handling utilities"""
import os
import uuid
import shutil
import tempfile
from typing import Optional, Tuple
from pathlib import Path
import PyPDF2
from ..config import config
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    @staticmethod
    def save_upload_file(file_content: bytes, original_filename: str) -> Tuple[str, str]:
        """Save uploaded file and return file path and job ID"""
        file_ext = Path(original_filename).suffix.lower()
        job_id = str(uuid.uuid4())
        safe_filename = f"{job_id}{file_ext}"
        
        if config.USE_GCP_SERVICES and config.GCP_BUCKET_NAME:
            try:
                from google.cloud import storage
                client = storage.Client(project=config.GCP_PROJECT) if config.GCP_PROJECT else storage.Client()
                bucket = client.bucket(config.GCP_BUCKET_NAME)
                blob = bucket.blob(f"uploads/{safe_filename}")
                blob.upload_from_string(file_content)
                logger.info(f"File uploaded to GCS: uploads/{safe_filename}")
                return f"gs://{config.GCP_BUCKET_NAME}/uploads/{safe_filename}", job_id
            except Exception as e:
                logger.warning(f"Failed to push to GCS, falling back to local: {e}")
        
        file_path = os.path.join(config.UPLOAD_DIR, safe_filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_path, job_id

    @staticmethod
    def _extract_local(file_path: str, file_ext: str) -> str:
        if file_ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif file_ext == ".csv":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif file_ext == ".pdf":
            text = ""
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
            return text
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")

    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        """Extract text from PDF, CSV, or TXT file"""
        file_ext = Path(file_path).suffix.lower()
        if not file_ext and file_path.startswith("gs://"):
             # basic heuristics for GCS blob paths without extension
             file_ext = Path(file_path.split("/")[-1]).suffix.lower()

        if file_path.startswith("gs://"):
            from google.cloud import storage
            client = storage.Client(project=config.GCP_PROJECT) if config.GCP_PROJECT else storage.Client()
            path_parts = file_path[5:].split('/', 1)
            bucket = client.bucket(path_parts[0])
            blob = bucket.blob(path_parts[1])
            
            fd, temp_path = tempfile.mkstemp(suffix=file_ext)
            os.close(fd)
            try:
                blob.download_to_filename(temp_path)
                return FileHandler._extract_local(temp_path, file_ext)
            finally:
                os.remove(temp_path)
        
        return FileHandler._extract_local(file_path, file_ext)
    
    @staticmethod
    def cleanup_temp_files(job_id: str):
        """Clean up temporary files for a job"""
        try:
            for f in Path(config.UPLOAD_DIR).glob(f"{job_id}.*"):
                os.remove(f)
            
            output_path = os.path.join(config.OUTPUT_DIR, job_id)
            if os.path.exists(output_path):
                shutil.rmtree(output_path)
        except Exception as e:
            logger.warning(f"Cleanup failed for {job_id}: {e}")
