"""Intent classification and routing"""
import logging
from typing import List
from .gemini_service import GeminiService

logger = logging.getLogger(__name__)

class IntentService:
    """Service for classifying and routing user intents"""
    
    def __init__(self):
        self.gemini_service = GeminiService()
    
    def classify(self, message: str) -> tuple:
        """Classify user intent"""
        if self.gemini_service.api_key:
            intent, confidence = self.gemini_service.understand_intent(message)
            keyword_intent = self._keyword_classify(message)

            # Recover from weak or failed LLM classification so the assistant
            # still answers obvious questions with the right intent.
            if intent == "general" and keyword_intent != "general":
                return keyword_intent, 0.65
            if confidence < 0.55 and keyword_intent != "general":
                return keyword_intent, 0.65

            return intent, confidence
        
        # Fallback keyword-based classification
        return self._keyword_classify(message), 0.6
    
    def _keyword_classify(self, message: str) -> str:
        """Simple keyword-based intent classification"""
        message_lower = message.lower()
        
        keywords = {
            "registration": ["register", "sign up", "enroll", "registration", "registered"],
            "deadlines": ["deadline", "when", "date", "timeline", "last day", "election day", "important dates"],
            "voting_methods": ["mail", "absentee", "early", "in person", "vote by", "voting options", "how can i vote"],
            "requirements": ["id", "document", "need", "require", "eligible", "qualify", "requirements"],
            "polling_locations": ["where", "polling place", "location", "site", "precinct"],
            "candidates": ["candidate", "ballot", "measure", "proposition", "who is running"]
        }
        
        for intent, words in keywords.items():
            if any(word in message_lower for word in words):
                return intent
        
        return "general"
    
    def get_follow_up_suggestions(self, intent: str) -> List[str]:
        """Get contextual follow-up questions based on intent"""
        suggestions = {
            "registration": [
                "How do I check my registration status?",
                "What's the registration deadline?",
                "Can I register online?"
            ],
            "deadlines": [
                "When is the primary election?",
                "What's the last day to request a mail ballot?",
                "When does early voting start?"
            ],
            "voting_methods": [
                "How do I request a mail ballot?",
                "Where can I vote early?",
                "What's the difference between absentee and mail voting?"
            ],
            "requirements": [
                "What ID do I need to vote?",
                "Can I vote if I just moved?",
                "Do I need to be a US citizen to vote?"
            ],
            "polling_locations": [
                "How do I find my polling place?",
                "What are polling place hours?",
                "Can I vote at any polling place?"
            ],
            "candidates": [
                "Where can I see a sample ballot?",
                "How do I research candidates?",
                "What ballot measures are on my ballot?"
            ],
            "general": [
                "How do I register to vote?",
                "When is Election Day?",
                "What are the voting options available to me?"
            ]
        }
        return suggestions.get(intent, suggestions["general"])
