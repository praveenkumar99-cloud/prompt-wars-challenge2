"""Module: assistant_service.py
Description: Main election assistant orchestrator.
Author: Praveen Kumar
"""
import logging
from typing import Dict, List, Optional

from ..config import config
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
from .intent_service import IntentService
from .timeline_service import TimelineService

logger = logging.getLogger(__name__)


class AssistantService:
    """Main election assistant orchestrator."""

    def __init__(self) -> None:
        """Initialize AssistantService with all required services."""
        self.gemini_service = GeminiService()
        self.intent_service = IntentService()
        self.timeline_service = TimelineService()

    async def process_message(self, message: str, session_id: Optional[str] = None) -> Dict:
        """Process user message and return assistant response.

        Args:
            message: User's question text.
            session_id: Optional session identifier for conversation tracking.

        Returns:
            Dictionary containing response, intent, follow-up suggestions, and sources.
        """
        logger.info("Processing message: %s...", message[:50])

        # Step 1: Classify intent
        intent, confidence = self.intent_service.classify(message)
        logger.info("Intent: %s (confidence: %s)", intent, confidence)

        # Step 2: Get context for intent
        context = self._get_context_for_intent(intent)

        # Step 3: Generate response
        if self.gemini_service.api_key:
            try:
                response_text = self.gemini_service.generate_response(message, intent, context)
            except Exception as e:
                # Broad catch to ensure fallback behavior if Gemini API fails
                logger.error("Response generation failed: %s", e)
                response_text = self._get_template_response(intent, context)
        else:
            response_text = self._get_template_response(intent, context)

        # Step 4: Get follow-up suggestions
        follow_ups = self.intent_service.get_follow_up_suggestions(intent)

        # Step 5: Get sources
        sources = self._get_sources(intent)

        # Persist session to Firestore
        try:
            from google.cloud import firestore

            db = firestore.Client(project=config.GCP_PROJECT_ID)
            db.collection(config.FIRESTORE_COLLECTION).document(
                session_id or "anonymous"
            ).set(
                {
                    "message": message,
                    "intent": intent,
                    "response": response_text,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                },
                merge=True,
            )
        except Exception as e:
            # Broad catch to avoid breaking user experience if Firestore unavailable
            logger.warning("Firestore write failed: %s", e)

        return {
            "response": response_text,
            "intent": intent,
            "follow_up_suggestions": follow_ups[:3],
            "sources": sources,
        }

    def _get_context_for_intent(self, intent: str) -> Dict:
        """Get relevant context based on intent.

        Args:
            intent: The classified intent category.

        Returns:
            Dictionary containing context information for the given intent.
        """
        context_map = {
            INTENT_REGISTRATION: {
                "description": "Register to vote online, by mail, or in-person",
                "deadline": "Varies by state, typically 15-30 days before Election Day",
                "requirements": "US citizen, state resident, 18+ by Election Day",
            },
            INTENT_DEADLINES: {
                "events": self.timeline_service.get_upcoming_events(),
                "registration_deadline": "Varies by state",
                "election_day": "November 5, 2024",
            },
            INTENT_VOTING_METHODS: {
                "options": ["In-person early", "In-person Election Day", "Vote by mail", "Absentee ballot"],
                "note": "Availability varies by state",
            },
            INTENT_REQUIREMENTS: {
                "id_requirements": "Varies by state - some require photo ID, others accept non-photo ID",
                "eligibility": "US citizen, state resident, 18+ by Election Day",
            },
            INTENT_POLLING_LOCATIONS: {
                "where_to_find": "Voter registration card or state election website",
                "typical_hours": "7 AM - 7 PM",
            },
            INTENT_CANDIDATES: {
                "where_to_find": "State election website for sample ballot"
            },
            INTENT_GENERAL: {
                "help_topics": [
                    "Registration",
                    "Deadlines",
                    "Voting methods",
                    "ID requirements",
                    "Polling places",
                ]
            },
        }
        return context_map.get(intent, context_map[INTENT_GENERAL])

    def _get_template_response(self, intent: str, context: Dict) -> str:
        """Template responses when Gemini is unavailable.

        Args:
            intent: The classified intent category.
            context: Context information (unused, kept for signature compatibility).

        Returns:
            Pre-written template response string.
        """
        templates = {
            INTENT_REGISTRATION: "To register to vote, you can register online, by mail, or in person. The deadline varies by state but is typically 15-30 days before Election Day. You'll need to be a US citizen, state resident, and at least 18 years old by Election Day.",
            INTENT_DEADLINES: f"Key upcoming election dates include: {', '.join([e.get('event', '') for e in self.timeline_service.get_upcoming_events()])}. Election Day is November 5, 2024. Check your state for specific registration deadlines.",
            INTENT_VOTING_METHODS: "You have several voting options: in-person early voting, in-person on Election Day, voting by mail, or absentee ballot. Availability varies by state.",
            INTENT_REQUIREMENTS: "Voter ID requirements vary by state. Some states require a government-issued photo ID, while others accept non-photo ID like a utility bill. First-time voters may need additional documentation.",
            INTENT_POLLING_LOCATIONS: "Find your polling place on your voter registration card or your state's election website. Polling places are typically open from 7 AM to 7 PM on Election Day.",
            INTENT_CANDIDATES: "To see candidates on your ballot, check your state's election website for a sample ballot. You can research candidates on Ballotpedia or Vote411.",
            INTENT_GENERAL: "I can help you with voter registration, election deadlines, voting methods, ID requirements, finding your polling place, and candidate information. What specific information do you need?",
        }
        return templates.get(intent, templates[INTENT_GENERAL])

    def _get_sources(self, intent: str) -> List[str]:
        """Get reliable sources for information.

        Args:
            intent: The classified intent category.

        Returns:
            List of source URL strings.
        """
        return [
            "USA.gov Voting & Election Information",
            "National Conference of State Legislatures",
            "Your State Election Office Website",
        ]
