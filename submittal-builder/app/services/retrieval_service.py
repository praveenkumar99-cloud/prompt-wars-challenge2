"""Document retrieval service (Vertex AI Search / Mock Fallback)"""
import json
import logging
import os
from typing import List, Dict, Tuple
from .gemini_service import GeminiService
from ..config import config

logger = logging.getLogger(__name__)

class RetrievalService:
    """Service for retrieving documents for part numbers"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.mock_docs = self._load_mock_docs()
    
    def _load_mock_docs(self) -> Dict[str, List[str]]:
        """Load mock document mapping"""
        mock_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "mock_docs.json")
        try:
            with open(mock_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load mock docs: {e}")
            return {}

    def _search_vertex_ai(self, part_number: str) -> List[str]:
        """Search Vertex AI Discovery Engine for documents"""
        if not config.GCP_PROJECT or not config.GCP_VERTEX_SEARCH_DATASTORE:
            return []
            
        try:
            from google.cloud import discoveryengine_v1alpha as discoveryengine
            client = discoveryengine.SearchServiceClient()
            
            serving_config = f"projects/{config.GCP_PROJECT}/locations/global/collections/default_collection/dataStores/{config.GCP_VERTEX_SEARCH_DATASTORE}/servingConfigs/default_search"
            
            request = discoveryengine.SearchRequest(
                serving_config=serving_config,
                query=part_number,
                page_size=5
            )
            
            response = client.search(request)
            found = []
            for result in response.results:
                docs = result.document.struct_data
                link = docs.get("link", result.document.name)
                if link:
                    found.append(link)
            return found
            
        except Exception as e:
            logger.warning(f"Vertex AI Search failed for {part_number}: {e}")
            return []
    
    def retrieve(self, part_number: str, validate: bool = True) -> Tuple[List[str], List[str]]:
        """Retrieve documents for a part number. Returns (found_docs, missing_docs)"""
        found = []
        
        # Try native GCP Enterprise Search first if configured
        if config.USE_GCP_SERVICES and config.GCP_VERTEX_SEARCH_DATASTORE:
            found = self._search_vertex_ai(part_number)
            
        # Fallback to local mocks
        if not found:
            found = self.mock_docs.get(part_number, [])
        
        if validate and self.gemini_service.api_key:
            validated = []
            for doc in found:
                relevant, confidence = self.gemini_service.validate_document_relevance(part_number, doc)
                if relevant and confidence > 0.5:
                    validated.append(doc)
                else:
                    logger.info(f"Document {doc} rejected for {part_number} (conf: {confidence})")
            found = validated
        
        missing = []
        if not found:
            missing.append(part_number)
        
        return found, missing
    
    def retrieve_batch(self, part_numbers: List[str], validate: bool = True) -> Dict[str, Dict]:
        """Retrieve documents for multiple part numbers"""
        results = {}
        for pn in part_numbers:
            found, missing = self.retrieve(pn, validate)
            results[pn] = {
                "found_documents": found,
                "is_missing": len(found) == 0,
                "document_count": len(found)
            }
        return results
