"""PDF generation utilities"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.fonts import addMapping
from ..config import config

class PDFGenerator:
    @staticmethod
    def generate_cover_page(job_id: str, part_numbers: list, output_path: str) -> str:
        """Generate a professional cover page for the submittal"""
        pdf_path = os.path.join(output_path, "cover_page.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a4d8c'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=20
        )
        
        story = []
        
        # Title
        story.append(Paragraph("PRODUCT SUBMITTAL PACKAGE", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Subtitle
        story.append(Paragraph(f"Job ID: {job_id}", subtitle_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Date
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        story.append(Paragraph("Package Summary", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"Total Parts Processed: {len(part_numbers)}", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        # Part numbers list
        story.append(Paragraph("Included Part Numbers:", styles['Heading3']))
        story.append(Spacer(1, 0.1*inch))
        
        for pn in part_numbers[:20]:  # Limit to first 20
            story.append(Paragraph(f"• {pn}", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))
        
        if len(part_numbers) > 20:
            story.append(Paragraph(f"... and {len(part_numbers) - 20} more", styles['Normal']))
        
        doc.build(story)
        return pdf_path
    
    @staticmethod
    def generate_toc(job_id: str, documents: dict, output_path: str) -> str:
        """Generate table of contents"""
        toc_path = os.path.join(output_path, "table_of_contents.txt")
        
        with open(toc_path, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("TABLE OF CONTENTS\n")
            f.write(f"Submittal Package: {job_id}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for part_number, docs in documents.items():
                f.write(f"\n{part_number}\n")
                f.write("-" * len(part_number) + "\n")
                for doc in docs:
                    f.write(f"  • {doc}\n")
        
        return toc_path
