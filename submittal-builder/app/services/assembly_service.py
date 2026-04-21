"""ZIP assembly and submittal packaging service"""
import os
import zipfile
import shutil
from typing import Dict, List
from datetime import datetime
from ..config import config
from ..utils.pdf_generator import PDFGenerator

class AssemblyService:
    """Service for assembling final submittal package"""
    
    def __init__(self):
        self.pdf_generator = PDFGenerator()
    
    def assemble(self, job_id: str, part_numbers: List[str], documents: Dict[str, List[str]], 
                 missing_parts: List[str]) -> str:
        """Assemble complete submittal package as ZIP file"""
        
        # Create job output directory
        job_output_dir = os.path.join(config.OUTPUT_DIR, job_id)
        os.makedirs(job_output_dir, exist_ok=True)
        
        # Generate cover page
        cover_path = self.pdf_generator.generate_cover_page(job_id, part_numbers, job_output_dir)
        
        # Generate TOC
        toc_path = self.pdf_generator.generate_toc(job_id, documents, job_output_dir)
        
        # Generate missing parts report
        missing_report_path = self._generate_missing_report(job_id, missing_parts, job_output_dir)
        
        # Create ZIP file
        zip_path = os.path.join(config.OUTPUT_DIR, f"{job_id}_submittal.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add cover page
            zipf.write(cover_path, arcname="01_cover_page.pdf")
            
            # Add TOC
            zipf.write(toc_path, arcname="02_table_of_contents.txt")
            
            # Add missing report if there are missing parts
            if missing_parts:
                zipf.write(missing_report_path, arcname="03_missing_parts_report.txt")
            
            # Add mock document placeholders for each part
            for part_number, docs in documents.items():
                part_dir = f"documents/{part_number}"
                for i, doc_name in enumerate(docs, 1):
                    # Create placeholder text file since we don't have real PDFs
                    placeholder_path = os.path.join(job_output_dir, f"{part_number}_{i}.txt")
                    with open(placeholder_path, "w") as f:
                        f.write(f"Document: {doc_name}\n")
                        f.write(f"Part Number: {part_number}\n")
                        f.write(f"This is a placeholder for {doc_name}\n")
                        f.write("In production, this would be the actual PDF document.\n")
                    zipf.write(placeholder_path, arcname=f"{part_dir}/{doc_name}.txt")
                    os.remove(placeholder_path)
        
        # Cleanup job directory
        shutil.rmtree(job_output_dir)
        
        return zip_path
    
    def _generate_missing_report(self, job_id: str, missing_parts: List[str], output_dir: str) -> str:
        """Generate missing parts report"""
        report_path = os.path.join(output_dir, "missing_parts.txt")
        
        with open(report_path, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("MISSING PARTS REPORT\n")
            f.write(f"Job ID: {job_id}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            if not missing_parts:
                f.write("No missing parts found.\n")
            else:
                f.write(f"Total missing parts: {len(missing_parts)}\n\n")
                for i, pn in enumerate(missing_parts, 1):
                    f.write(f"{i}. {pn}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("ACTION REQUIRED: Please source documentation for missing parts.\n")
        
        return report_path
