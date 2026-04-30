"""Module: vertex_ai_service.py
Description: Vertex AI SDK integration for enhanced generative capabilities.
Author: Praveen Kumar
"""
import json
import logging
from typing import Optional, Tuple

from ..config import config

logger = logging.getLogger(__name__)


class VertexAIService:
    """Service for interacting with Google Vertex AI generative models."""

    def __init__(self) -> None:
        """Initialize VertexAIService with lazy client initialization."""
        self._client: Optional[object] = None
        self._initialized: bool = False

    def _initialize_client(self) -> bool:
        """Initialize Vertex AI client.

        Returns:
            bool: True if initialization successful, False otherwise.

        Raises:
            Exception: If client initialization fails.
        """
        if self._initialized:
            return self._client is not None

        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            vertexai.init(
                project=config.GCP_PROJECT_ID,
                location=config.VERTEX_AI_LOCATION,
            )
            self._client = GenerativeModel("gemini-2.5-pro")
            self._initialized = True
            logger.info("Vertex AI initialized successfully")
            return True
        except Exception as e:
            logger.error("Vertex AI initialization failed: %s", e)
            self._initialized = True
            self._client = None
            return False

    def understand_intent_advanced(
        self, message: str, context: Optional[str] = None
    ) -> Tuple[str, float]:
        """Classify user intent using Vertex AI with advanced context.

        Args:
            message: User's question text.
            context: Optional conversation context.

        Returns:
            Tuple of (intent_category, confidence_score).
        """
        if not config.ENABLE_VERTEX_AI or not self._initialize_client():
            return "general", 0.5

        try:
            prompt = """
            Classify the user's election-related question into one of these categories:
            - registration: Questions about registering to vote
            - deadlines: Questions about election dates and deadlines
            - voting_methods: Questions about how to vote (mail, early, in-person)
            - requirements: Questions about voter ID, eligibility, documents
            - polling_locations: Questions about where to vote
            - candidates: Questions about candidates or ballot measures
            - general: Other election-related questions

            Message: "%s"
            %s

            Output ONLY JSON: {"intent": "category", "confidence": 0.0-1.0}
            """ % (message, f"Context: {context}" if context else "")

            response = self._client.generate_content(prompt)
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
            logger.warning("Vertex AI intent classification failed: %s", e)
            return "general", 0.5

    def generate_response_advanced(
        self, message: str, intent: str, context: dict
    ) -> str:
        """Generate response using Vertex AI with structured context.

        Args:
            message: User's original question.
            intent: Classified intent category.
            context: Relevant context information.

        Returns:
            Generated response text, or fallback on error.
        """
        if not config.ENABLE_VERTEX_AI or not self._initialize_client():
            return "Unable to generate response at this time."

        try:
            context_str = json.dumps(context, indent=2)

            prompt = """
            You are a helpful, non-partisan election assistant for USA elections.
            
            Intent: %s
            Context: %s
            
            User Question: "%s"
            
            Provide a clear, factual, non-partisan response. Keep it concise (2-3 sentences).
            """ % (intent, context_str, message)

            response = self._client.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error("Vertex AI response generation failed: %s", e)
            return "I apologize, but I'm unable to generate a response at this time."

    def generate_follow_ups_advanced(self, intent: str) -> list:
        """Generate contextual follow-up suggestions using Vertex AI.

        Args:
            intent: Current conversation intent.

        Returns:
            List of follow-up question suggestions.
        """
        if not config.ENABLE_VERTEX_AI or not self._initialize_client():
            return []

        try:
            prompt = """
            Generate 3 natural follow-up questions for a user interested in: %s
            
            Return ONLY a JSON array of strings: ["question1", "question2", "question3"]
            """ % intent

            response = self._client.generate_content(prompt)
            raw = response.text.strip()

            if raw.startswith("```"):
                raw = raw.split("```")[1].strip()
                if raw.startswith("json"):
                    raw = raw[4:].strip()

            questions = json.loads(raw)
            return questions if isinstance(questions, list) else []

        except Exception as e:
            logger.warning("Vertex AI follow-up generation failed: %s", e)
            return []

    def batch_process_messages(
        self, messages: list
    ) -> list:
        """Process multiple messages in batch using Vertex AI.

        Args:
            messages: List of message dictionaries with 'text' and 'intent' keys.

        Returns:
            List of processed results with responses.
        """
        if not config.ENABLE_VERTEX_AI or not self._initialize_client():
            return []

        results = []
        try:
            for msg in messages:
                response = self.generate_response_advanced(
                    msg.get("text", ""),
                    msg.get("intent", "general"),
                    msg.get("context", {}),
                )
                results.append({"text": msg.get("text"), "response": response})
        except Exception as e:
            logger.error("Batch processing failed: %s", e)

        return results
