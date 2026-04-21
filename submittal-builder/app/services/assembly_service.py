"""ZIP assembly and submittal packaging service"""
import os
import zipfile
import shutil
import logging
from typing import Dict, List
from datetime import datetime
from ..config import config
from ..utils.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)

class AssemblyService:
    """Service for assembling final submittal package"""
    
    def __init__(self):
        self.pdf_generator = PDFGenerator()
    
    def assemble(self, job_id: str, part_numbers: List[str], documents: Dict[str, List[str]], 
                 missing_parts: List[str]) -> str:
        """Assemble complete submittal package as ZIP file"""
        
        job_output_dir = os.path.join(config.OUTPUT_DIR, job_id)
        os.makedirs(job_output_dir, exist_ok=True)
        
        cover_path = self.pdf_generator.generate_cover_page(job_id, part_numbers, job_output_dir)
        toc_path = self.pdf_generator.generate_toc(job_id, documents, job_output_dir)
        missing_report_path = self._generate_missing_report(job_id, missing_parts, job_output_dir)
        
        zip_filename = f"{job_id}_submittal.zip"
        zip_path = os.path.join(config.OUTPUT_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(cover_path, arcname="01_cover_page.pdf")
            zipf.write(toc_path, arcname="02_table_of_contents.txt")
            if missing_parts:
                zipf.write(missing_report_path, arcname="03_missing_parts_report.txt")
            
            for part_number, docs in documents.items():
                part_dir = f"documents/{part_number}"
                for i, doc_name in enumerate(docs, 1):
                    placeholder_path = os.path.join(job_output_dir, f"{part_number}_{i}.txt")
                    with open(placeholder_path, "w") as f:
                        f.write(f"Document: {doc_name}\nPart Number: {part_number}\nThis is a placeholder.\n")
                    zipf.write(placeholder_path, arcname=f"{part_dir}/{doc_name}.txt")
                    os.remove(placeholder_path)
        
        shutil.rmtree(job_output_dir)
        
        # If GCP is enabled, upload the zip to GCS.
        if config.USE_GCP_SERVICES and config.GCP_BUCKET_NAME:
            try:
                from google.cloud import storage
                client = storage.Client(project=config.GCP_PROJECT) if config.GCP_PROJECT else storage.Client()
                bucket = client.bucket(config.GCP_BUCKET_NAME)
                blob = bucket.blob(f"outputs/{zip_filename}")
                blob.upload_from_filename(zip_path)
                logger.info(f"ZIP uploaded to GCS: outputs/{zip_filename}")
                # We can return GCS zip path
                return f"gs://{config.GCP_BUCKET_NAME}/outputs/{zip_filename}"
            except Exception as e:
                logger.warning(f"Failed to upload ZIP to GCS, falling back to local: {e}")
        
        return zip_path
    
    def _generate_missing_report(self, job_id: str, missing_parts: List[str], output_dir: str) -> str:
        report_path = os.path.join(output_dir, "missing_parts.txt")
        with open(report_path, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("MISSING PARTS REPORT\n")
            f.write(f"Job ID: {job_id}\n Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            if not missing_parts:
                f.write("No missing parts found.\n")
            else:
                f.write(f"Total missing parts: {len(missing_parts)}\n\n")
                for i, pn in enumerate(missing_parts, 1):
                    f.write(f"{i}. {pn}\n")
        return report_path
