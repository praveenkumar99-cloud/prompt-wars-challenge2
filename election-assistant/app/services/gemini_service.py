"""Gemini LLM integration for election assistance"""
import json
import logging
from typing import Tuple, List, Dict
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
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                raise
        return self._client
    
    def understand_intent(self, message: str) -> Tuple[str, float]:
        """Classify user intent from message"""
        client = self._get_client()
        
        prompt = f"""
        Classify the user's election-related question into one of these categories:
        - registration: Questions about registering to vote
        - deadlines: Questions about election dates and deadlines
        - voting_methods: Questions about how to vote (mail, early, in-person)
        - requirements: Questions about voter ID, eligibility, documents
        - polling_locations: Questions about where to vote
        - candidates: Questions about candidates or ballot measures
        - general: Other election-related questions
        
        Message: "{message}"
        
        Output ONLY JSON: {{"intent": "category", "confidence": 0.0-1.0}}
        """
        
        try:
            response = client.generate_content(prompt)
            raw = response.text.strip()
            
            if raw.startswith("```json"):
                raw = raw[7:]
            if raw.startswith("```"):
                raw = raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            
            data = json.loads(raw)
            return data.get("intent", "general"), data.get("confidence", 0.7)
            
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}")
            return "general", 0.5
    
    def generate_response(self, message: str, intent: str, context: Dict) -> str:
        """Generate a helpful, conversational response"""
        client = self._get_client()
        
        prompt = f"""
        You are a helpful, non-partisan election assistant. Provide clear, accurate information.
        
        User Question: {message}
        Intent Category: {intent}
        Available Information: {json.dumps(context)}
        
        Guidelines:
        1. Be factual and unbiased
        2. Note when rules vary by state
        3. Suggest specific next steps
        4. Keep response conversational but informative
        5. Do not express political opinions
        
        Generate a helpful response:
        """
        
        try:
            response = client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return self._get_fallback_response(intent)
    
    def _get_fallback_response(self, intent: str) -> str:
        """Fallback responses when Gemini is unavailable"""
        fallbacks = {
            "registration": "To register to vote, check your state's election website. Most states offer online registration. You'll need to be a US citizen, state resident, and at least 18 years old by Election Day.",
            "deadlines": "Election deadlines vary by state. Key dates include voter registration deadlines (typically 15-30 days before Election Day), early voting periods, and mail ballot request deadlines.",
            "voting_methods": "You can vote in person on Election Day, vote early at designated locations, or vote by mail. Check your state's options.",
            "requirements": "Voter ID requirements vary by state. Some require photo ID, others accept non-photo ID or no ID. First-time voters may need additional documentation.",
            "polling_locations": "Find your polling place on your voter registration card or your state's election website. Hours are typically 7 AM to 7 PM.",
            "candidates": "Check your state's official election website for a sample ballot showing all candidates and measures.",
            "general": "I can help with voter registration, election deadlines, voting methods, ID requirements, and finding your polling place. What would you like to know?"
        }
        return fallbacks.get(intent, fallbacks["general"])
