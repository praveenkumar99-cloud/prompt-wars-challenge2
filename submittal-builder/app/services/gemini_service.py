"""Gemini LLM integration using Vertex AI"""
import json
import logging
from typing import List, Dict, Tuple
from ..config import config

logger = logging.getLogger(__name__)

class GeminiService:
    """Service for interacting with Google's Gemini LLM"""
    
    def __init__(self):
        self.model_name = config.GEMINI_MODEL
        self.api_key = config.GOOGLE_API_KEY
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of Gemini client"""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model_name)
                logger.info("Gemini client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
                raise
        return self._client
    
    def extract_part_numbers(self, text: str) -> Tuple[List[str], str]:
        """Extract part numbers from BOM text using Gemini"""
        client = self._get_client()
        
        prompt = f"""
        Extract all unique product part numbers from this Bill of Materials (BOM) text.
        
        Rules:
        1. Part numbers typically contain letters, numbers, and hyphens
        2. Look for patterns like XXX-999, XXX-999-XX, or alphanumeric codes
        3. Ignore quantities, descriptions, and non-part-number values
        4. Remove duplicates
        5. Output ONLY valid JSON format: {{"part_numbers": ["PN1", "PN2", ...]}}
        
        BOM Text:
        {text[:15000]}  # Limit text length
        
        Return ONLY the JSON object, no other text.
        """
        
        try:
            response = client.generate_content(prompt)
            raw_response = response.text
            
            # Clean and parse JSON
            clean_json = raw_response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.startswith("```"):
                clean_json = clean_json[3:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            
            data = json.loads(clean_json.strip())
            part_numbers = data.get("part_numbers", [])
            
            logger.info(f"Extracted {len(part_numbers)} part numbers")
            return part_numbers, raw_response
            
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            # Fallback to regex pattern matching
            import re
            pattern = r'[A-Z]{2,4}-\d{3,4}(?:-[A-Z0-9]{2,4})?'
            fallback_parts = list(set(re.findall(pattern, text)))
            logger.info(f"Fallback extraction found {len(fallback_parts)} parts")
            return fallback_parts, f"Fallback extraction: {e}"
    
    def validate_document_relevance(self, part_number: str, document_name: str) -> Tuple[bool, float]:
        """Validate if a document is relevant for a given part number"""
        client = self._get_client()
        
        prompt = f"""
        Determine if this document is relevant for the given part number.
        
        Part Number: {part_number}
        Document Name: {document_name}
        
        Output ONLY JSON: {{"relevant": true/false, "confidence": 0.0-1.0}}
        """
        
        try:
            response = client.generate_content(prompt)
            raw = response.text.strip()
            
            # Clean JSON
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            
            data = json.loads(raw)
            return data.get("relevant", False), data.get("confidence", 0.5)
            
        except Exception as e:
            logger.warning(f"Validation failed for {part_number}/{document_name}: {e}")
            # Default to relevant with moderate confidence
            return True, 0.6
