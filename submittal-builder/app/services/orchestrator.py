"""Main orchestrator coordinating all services"""
import logging
from typing import Dict, List, Tuple
from datetime import datetime
from .extraction_service import ExtractionService
from .retrieval_service import RetrievalService
from .assembly_service import AssemblyService

logger = logging.getLogger(__name__)

class Orchestrator:
    """Orchestrates the entire submittal generation workflow"""
    
    def __init__(self):
        self.extraction_service = ExtractionService()
        self.retrieval_service = RetrievalService()
        self.assembly_service = AssemblyService()
    
    def process(self, job_id: str, text: str) -> Tuple[str, List[str], Dict]:
        """
        Process a BOM and generate submittal package.
        Returns: (zip_path, missing_parts, documents_map)
        """
        logger.info(f"Starting orchestration for job {job_id}")
        
        # Step 1: Extract part numbers
        logger.info("Extracting part numbers...")
        part_numbers = self.extraction_service.extract(text)
        logger.info(f"Extracted {len(part_numbers)} part numbers: {part_numbers}")
        
        # Step 2: Retrieve documents for each part
        logger.info("Retrieving documents...")
        documents_map = {}
        missing_parts = []
        
        for pn in part_numbers:
            found, missing = self.retrieval_service.retrieve(pn, validate=True)
            documents_map[pn] = found
            if missing:
                missing_parts.extend(missing)
        
        logger.info(f"Found documents for {len([k for k,v in documents_map.items() if v])} parts")
        logger.info(f"Missing {len(missing_parts)} parts: {missing_parts}")
        
        # Step 3: Assemble final package
        logger.info("Assembling submittal package...")
        zip_path = self.assembly_service.assemble(job_id, part_numbers, documents_map, missing_parts)
        
        logger.info(f"Orchestration complete for job {job_id}")
        return zip_path, missing_parts, documents_map
