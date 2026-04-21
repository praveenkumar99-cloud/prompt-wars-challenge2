"""Part number extraction service"""
import re
import logging
from typing import List, Set
from .gemini_service import GeminiService

logger = logging.getLogger(__name__)

class ExtractionService:
    """Service for extracting and normalizing part numbers"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
    
    def extract(self, text: str, use_gemini: bool = True) -> List[str]:
        """Extract part numbers from text"""
        if use_gemini and self.gemini_service.api_key:
            parts, _ = self.gemini_service.extract_part_numbers(text)
            if parts:
                return self._normalize(parts)
        
        # Fallback regex extraction
        return self._regex_extract(text)
    
    def _regex_extract(self, text: str) -> List[str]:
        """Extract using regex patterns"""
        patterns = [
            r'[A-Z]{2,5}-\d{3,5}(?:-[A-Z0-9]{2,5})?',  # PWR-4000-XL
            r'[A-Z]{3,6}-\d{3,6}',  # CTL-MOD-128
            r'[A-Z]{3,5}-\d{2,4}-[A-Z]{2,5}',  # CBL-HARNESS-05
            r'[A-Z]{3,5}-\d{3,4}',  # SNS-TEMP-PT100
        ]
        
        all_matches = set()
        for pattern in patterns:
            matches = re.findall(pattern, text)
            all_matches.update(matches)
        
        return self._normalize(list(all_matches))
    
    def _normalize(self, part_numbers: List[str]) -> List[str]:
        """Normalize part numbers (uppercase, strip whitespace)"""
        normalized = []
        seen = set()
        
        for pn in part_numbers:
            clean = pn.strip().upper()
            if clean and clean not in seen:
                seen.add(clean)
                normalized.append(clean)
        
        return normalized
