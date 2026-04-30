"""Module: assistant_service.py
Description: Main election assistant orchestrator with Vertex AI and multi-service integration.
Author: Praveen Kumar
"""
import hashlib
import logging
import uuid
from typing import Any, Dict, List, Optional

from ..config import config
from ..constants import (
    INTENT_CANDIDATES,
    INTENT_DEADLINES,
    INTENT_GENERAL,
    INTENT_POLLING_LOCATIONS,
    INTENT_REGISTRATION,
    INTENT_REQUIREMENTS,
    INTENT_VOTING_METHODS,
    LOG_INTENT_CLASSIFICATION_FAILED,
    LOG_RESPONSE_GENERATION_FAILED,
)
from .audit_service import AuditService
from .cache_service import CacheService
from .gemini_service import GeminiService
from .intent_service import IntentService
from .timeline_service import TimelineService
from .vertex_ai_service import VertexAIService

try:
    from google.cloud import firestore as firestore_client
except ImportError:
    firestore_client = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class AssistantService:
    """Main election assistant orchestrator with full GCP integration."""

    def __init__(self) -> None:
        """Initialize AssistantService with all required services.

        Initializes:
        - GeminiService for basic LLM capabilities
        - VertexAIService for advanced generative features
        - IntentService for message classification
        - TimelineService for event data
        - CacheService for performance optimization
        - AuditService for compliance logging
        """
        self.gemini_service: GeminiService = GeminiService()
        self.vertex_ai_service: VertexAIService = VertexAIService()
        self.intent_service: IntentService = IntentService()
        self.timeline_service: TimelineService = TimelineService()
        self.cache_service: CacheService = CacheService()
        self.audit_service: AuditService = AuditService()
        self.conversation_history: Dict[str, List[Dict[str, str]]] = {}  # Store last 5 messages per session

    def get_conversation_context(self, session_id: str) -> str:
        """Get recent conversation history as formatted context string.

        Retrieves the last 3 exchanges for a given session and formats
        them as a readable conversation string for LLM context injection.

        Args:
            session_id: Unique session identifier.

        Returns:
            Formatted conversation history string, or empty string
            if no history exists for the session.
        """
        if session_id not in self.conversation_history:
            return ""
        history = self.conversation_history[session_id][-3:]  # Last 3 exchanges
        context = "\n".join(["User: %s\nAssistant: %s" % (h["user"], h["assistant"]) for h in history])
        return "Previous conversation:\n%s\n\n" % context

    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """Process user message and return assistant response with full integration.

        Args:
            message: User's question text.
            session_id: Optional session identifier for conversation tracking.
            language: Language code (en/es) for response.

        Returns:
            Dictionary containing response, intent, follow-up suggestions, and sources.

        Raises:
            Exception: On critical processing failures (propagated to route handler).
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        # Get conversation context
        context = self.get_conversation_context(session_id)

        # Enhance prompt with context
        enhanced_message = f"{context}User question: {message}"

        logger.info(
            "Processing message (lang=%s, session=%s): %s...",
            language,
            session_id,
            message[:50],
        )

        # Check cache for identical messages
        message_hash = hashlib.md5(enhanced_message.encode()).hexdigest()
        cached_intent = self.cache_service.get_intent_result(message_hash)

        # Step 1: Classify intent (use cache if available)
        if cached_intent:
            intent = cached_intent.get("intent", "general")
            confidence = cached_intent.get("confidence", 0.7)
            logger.debug("Using cached intent classification")
        else:
            try:
                intent, confidence = self.intent_service.classify(enhanced_message, context)
                # Cache the result
                self.cache_service.set_intent_result(message_hash, intent, confidence)
            except Exception as e:
                logger.error(LOG_INTENT_CLASSIFICATION_FAILED, e)
                intent = INTENT_GENERAL
                confidence = 0.5

        logger.info("Intent: %s (confidence: %.2f)", intent, confidence)

        # Step 2: Get context for intent
        intent_context = self._get_context_for_intent(intent)

        # Step 3: Generate response (prefer Vertex AI if available)
        try:
            if config.ENABLE_VERTEX_AI and self.vertex_ai_service._initialize_client():
                logger.debug("Using Vertex AI for response generation")
                response_text = (
                    self.vertex_ai_service.generate_response_advanced(
                        enhanced_message, intent, intent_context
                    )
                )
            elif self.gemini_service.api_key:
                logger.debug("Using Gemini for response generation")
                response_text = self.gemini_service.generate_response(
                    enhanced_message, intent, intent_context, context
                )
            else:
                logger.debug("Using template response")
                response_text = self._get_template_response(intent, intent_context)
        except Exception as e:
            logger.error(LOG_RESPONSE_GENERATION_FAILED, e)
            response_text = self._get_template_response(intent, context)

        # Step 4: Get follow-up suggestions
        try:
            if config.ENABLE_VERTEX_AI:
                follow_ups = (
                    self.vertex_ai_service.generate_follow_ups_advanced(intent)
                )
            else:
                follow_ups = self.intent_service.get_follow_up_suggestions(intent)
        except Exception as e:
            logger.warning("Follow-up generation failed: %s", e)
            follow_ups = self.intent_service.get_follow_up_suggestions(intent)

        # Step 5: Get sources
        sources = self._get_sources(intent)

        # Step 6: Persist session to Firestore
        if config.ENABLE_FIRESTORE and session_id:
            try:
                if firestore_client is None:
                    logger.warning("Firestore client not available")
                else:
                    db = firestore_client.Client(project=config.GCP_PROJECT_ID)
                    db.collection(config.FIRESTORE_COLLECTION).document(session_id).set(
                        {
                            "message": message,
                            "intent": intent,
                            "response": response_text[:500],
                            "language": language,
                            "confidence": confidence,
                            "timestamp": firestore_client.SERVER_TIMESTAMP,
                        },
                        merge=True,
                    )
                    logger.debug("Session persisted to Firestore: %s", session_id)
            except Exception as e:
                logger.warning("Firestore write failed: %s", e)

        # Store in history
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        self.conversation_history[session_id].append({"user": message, "assistant": response_text})
        # Keep only last 5
        self.conversation_history[session_id] = self.conversation_history[session_id][-5:]

        result = {
            "response": response_text,
            "intent": intent,
            "follow_up_suggestions": follow_ups[:3],
            "sources": sources,
            "session_id": session_id
        }

        logger.info("Message processed successfully for session: %s", session_id)
        return result

    def _get_context_for_intent(self, intent: str) -> Dict[str, Any]:
        """Get relevant context based on classified intent.

        Args:
            intent: The classified intent category.

        Returns:
            Dictionary containing context information for the given intent.
        """
        context_map: Dict[str, Dict[str, Any]] = {
            INTENT_REGISTRATION: {
                "description": "Register to vote online, by mail, or in-person",
                "deadline": "Varies by state, typically 15-30 days before Election Day",
                "requirements": "US citizen, state resident, 18+ by Election Day",
                "resources": [
                    "usa.gov/register-to-vote",
                    "vote411.org",
                    "ballotpedia.org",
                ],
            },
            INTENT_DEADLINES: {
                "events": self.timeline_service.get_upcoming_events(),
                "registration_deadline": "Varies by state",
                "early_voting_period": "Varies by state",
                "election_day": "November 5, 2024",
            },
            INTENT_VOTING_METHODS: {
                "options": [
                    "In-person early",
                    "In-person Election Day",
                    "Vote by mail",
                    "Absentee ballot",
                ],
                "note": "Availability varies by state",
                "resources": ["your state election office website"],
            },
            INTENT_REQUIREMENTS: {
                "id_requirements": "Varies by state - some require photo ID",
                "eligibility": "US citizen, state resident, 18+ by Election Day",
                "documentation": "May include voter registration card, utility bill",
            },
            INTENT_POLLING_LOCATIONS: {
                "where_to_find": "Voter registration card or state election website",
                "typical_hours": "7 AM - 7 PM",
                "what_to_bring": "ID (requirements vary) and voter registration card",
                "civic_api": "Use Google Civic API for location data",
            },
            INTENT_CANDIDATES: {
                "where_to_find": "State election website for sample ballot",
                "research_tools": ["Ballotpedia", "Vote411", "league of women voters"],
            },
            INTENT_GENERAL: {
                "help_topics": [
                    "Registration",
                    "Deadlines",
                    "Voting methods",
                    "ID requirements",
                    "Polling places",
                    "Candidates",
                ]
            },
        }
        return context_map.get(intent, context_map[INTENT_GENERAL])

    def _get_template_response(self, intent: str, context: Dict[str, Any]) -> str:
        """Template responses when LLMs are unavailable.

        Args:
            intent: The classified intent category.
            context: Context information.

        Returns:
            Pre-written template response string.
        """
        templates: Dict[str, str] = {
            INTENT_REGISTRATION: (
                "To register to vote, you can register online, by mail, or in person. "
                "The deadline varies by state but is typically 15-30 days before Election Day. "
                "You'll need to be a US citizen, state resident, and at least 18 years old by Election Day. "
                "Visit usa.gov/register-to-vote for your state's specific registration process."
            ),
            INTENT_DEADLINES: (
                "Key upcoming election dates: Registration deadlines vary by state. "
                "Most states have deadlines 15-30 days before Election Day. "
                "Election Day is November 5, 2024. Early voting periods also vary by state. "
                "Check your state election office website for exact dates."
            ),
            INTENT_VOTING_METHODS: (
                "You have several voting options: in-person early voting, "
                "in-person on Election Day, voting by mail, or absentee ballot. "
                "Availability and requirements vary by state. "
                "Contact your state election office for details."
            ),
            INTENT_REQUIREMENTS: (
                "Voter ID requirements vary by state. Some states require a government-issued photo ID, "
                "while others accept non-photo ID like a utility bill or voter registration card. "
                "First-time voters may need additional documentation. Check your state's requirements."
            ),
            INTENT_POLLING_LOCATIONS: (
                "Find your polling place on your voter registration card or your state's election website. "
                "Polling places are typically open from 7 AM to 7 PM on Election Day. "
                "Bring your ID (requirements vary) and voter registration card if you have it."
            ),
            INTENT_CANDIDATES: (
                "To see candidates on your ballot and research them, check your state's election website "
                "for a sample ballot. You can also use resources like Ballotpedia, Vote411, or the "
                "League of Women Voters for candidate information."
            ),
            INTENT_GENERAL: (
                "I can help you with voter registration, election deadlines, voting methods, "
                "ID requirements, finding your polling place, and candidate information. "
                "What specific information do you need?"
            ),
        }
        return templates.get(intent, templates[INTENT_GENERAL])

    def _get_sources(self, intent: str) -> List[str]:
        """Get reliable sources for information based on intent.

        Args:
            intent: The classified intent category.

        Returns:
            List of source names/URLs.
        """
        base_sources = [
            "USA.gov - Voting & Election Information",
            "Your State Election Office",
            "Vote411.org",
        ]

        intent_sources: Dict[str, List[str]] = {
            INTENT_CANDIDATES: base_sources + ["Ballotpedia", "League of Women Voters"],
            INTENT_POLLING_LOCATIONS: base_sources + ["Google Civic API"],
            INTENT_REGISTRATION: base_sources + ["ImmigrationProof"],
        }

        return intent_sources.get(intent, base_sources)
