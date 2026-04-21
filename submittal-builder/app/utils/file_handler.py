"""File handling utilities"""
import os
import uuid
import shutil
from typing import Optional, Tuple
from pathlib import Path
import PyPDF2
from ..config import config

class FileHandler:
    @staticmethod
    def save_upload_file(file_content: bytes, original_filename: str) -> Tuple[str, str]:
        """Save uploaded file and return file path and job ID"""
        file_ext = Path(original_filename).suffix.lower()
        job_id = str(uuid.uuid4())
        safe_filename = f"{job_id}{file_ext}"
        file_path = os.path.join(config.UPLOAD_DIR, safe_filename)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_path, job_id
    
    @staticmethod
    def extract_text_from_file(file_path: str) -> str:
        """Extract text from PDF, CSV, or TXT file"""
        file_ext = Path(file_path).suffix.lower()
        
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
                    text += page.extract_text()
            return text
        
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    @staticmethod
    def cleanup_temp_files(job_id: str):
        """Clean up temporary files for a job"""
        upload_pattern = os.path.join(config.UPLOAD_DIR, f"{job_id}.*")
        output_path = os.path.join(config.OUTPUT_DIR, job_id)
        
        for f in Path(config.UPLOAD_DIR).glob(f"{job_id}.*"):
            os.remove(f)
        
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
