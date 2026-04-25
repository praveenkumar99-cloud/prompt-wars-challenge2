"""Module: intent_service.py
Description: Intent classification and routing service.
Author: Praveen Kumar
"""
import logging
from typing import List, Tuple

from ..constants import (
    INTENT_CANDIDATES,
    INTENT_DEADLINES,
    INTENT_GENERAL,
    INTENT_POLLING_LOCATIONS,
    INTENT_REGISTRATION,
    INTENT_REQUIREMENTS,
    INTENT_VOTING_METHODS,
)
from .gemini_service import GeminiService

logger = logging.getLogger(__name__)


class IntentService:
    """Service for classifying and routing user intents."""

    def __init__(self) -> None:
        """Initialize IntentService with GeminiService instance."""
        self.gemini_service = GeminiService()

    def classify(self, message: str, context: str = "") -> Tuple[str, float]:
        """Classify user intent using LLM with keyword fallback.

        Args:
            message: User's question text.
            context: Previous conversation context.

        Returns:
            Tuple of (intent_category, confidence_score).
            Falls back to keyword classification if LLM is unavailable
            or confidence is too low.
        """
        if self.gemini_service.api_key:
            intent, confidence = self.gemini_service.understand_intent(message, context)
            keyword_intent = self._keyword_classify(message)

            # Recover from weak or failed LLM classification so the assistant
            # still answers obvious questions with the right intent.
            if intent == INTENT_GENERAL and keyword_intent != INTENT_GENERAL:
                return keyword_intent, 0.65
            if confidence < 0.55 and keyword_intent != INTENT_GENERAL:
                return keyword_intent, 0.65

            return intent, confidence

        # Fallback keyword-based classification
        return self._keyword_classify(message), 0.6

    def _keyword_classify(self, message: str) -> str:
        """Simple keyword-based intent classification.

        Args:
            message: User's question text.

        Returns:
            Intent category string.
        """
        message_lower = message.lower()

        keywords = {
            INTENT_REGISTRATION: [
                "register",
                "sign up",
                "enroll",
                "registration",
                "registered",
            ],
            INTENT_DEADLINES: [
                "deadline",
                "when",
                "date",
                "timeline",
                "last day",
                "election day",
                "important dates",
            ],
            INTENT_VOTING_METHODS: [
                "mail",
                "absentee",
                "early",
                "in person",
                "vote by",
                "voting options",
                "how can i vote",
            ],
            INTENT_REQUIREMENTS: [
                "id",
                "document",
                "need",
                "require",
                "eligible",
                "qualify",
                "requirements",
            ],
            INTENT_POLLING_LOCATIONS: [
                "where",
                "polling place",
                "location",
                "site",
                "precinct",
            ],
            INTENT_CANDIDATES: ["candidate", "ballot", "measure", "proposition", "who is running"],
        }

        for intent, words in keywords.items():
            if any(word in message_lower for word in words):
                return intent

        return INTENT_GENERAL

    def get_follow_up_suggestions(self, intent: str) -> List[str]:
        """Get contextual follow-up questions based on intent.

        Args:
            intent: The classified intent category.

        Returns:
            List of suggested follow-up question strings.
        """
        suggestions = {
            INTENT_REGISTRATION: [
                "How do I check my registration status?",
                "What's the registration deadline?",
                "Can I register online?",
            ],
            INTENT_DEADLINES: [
                "When is the primary election?",
                "What's the last day to request a mail ballot?",
                "When does early voting start?",
            ],
            INTENT_VOTING_METHODS: [
                "How do I request a mail ballot?",
                "Where can I vote early?",
                "What's the difference between absentee and mail voting?",
            ],
            INTENT_REQUIREMENTS: [
                "What ID do I need to vote?",
                "Can I vote if I just moved?",
                "Do I need to be a US citizen to vote?",
            ],
            INTENT_POLLING_LOCATIONS: [
                "How do I find my polling place?",
                "What are polling place hours?",
                "Can I vote at any polling place?",
            ],
            INTENT_CANDIDATES: [
                "Where can I see a sample ballot?",
                "How do I research candidates?",
                "What ballot measures are on my ballot?",
            ],
            INTENT_GENERAL: [
                "How do I register to vote?",
                "When is Election Day?",
                "What are the voting options available to me?",
            ],
        }
        return suggestions.get(intent, suggestions[INTENT_GENERAL])
