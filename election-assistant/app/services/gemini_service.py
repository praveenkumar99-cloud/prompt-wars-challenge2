"""Module: gemini_service.py
Description: Gemini LLM integration for election assistance.
Author: Praveen Kumar
"""
__all__ = ["GeminiService"]

import asyncio
import json
import logging
from typing import Optional, Tuple

from ..config import config

logger = logging.getLogger(__name__)

# Timeout for LLM API calls (seconds)
LLM_TIMEOUT = 8


class GeminiService:
    """Service for interacting with Google's Gemini LLM."""

    api_key: str = (config.GOOGLE_API_KEY or "").strip()
    model_name: str = config.GEMINI_MODEL

    def __init__(self) -> None:
        """Initialize GeminiService with lazy client initialization."""
        self._client = None

    def _get_client(self):
        """Lazy initialization of Gemini client.

        Returns:
            GenerativeModel: Configured Gemini model instance.

        Raises:
            Exception: If client initialization fails.
        """
        if self._client is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model_name)
                logger.info("Gemini client initialized")
            except Exception as e:
                logger.error("Failed to initialize Gemini: %s", e)
                raise
        return self._client

    def understand_intent(self, message: str, context: str = "") -> Tuple[str, float]:
        """Classify user intent from message using Gemini.

        Args:
            message: User's question text.
            context: Previous conversation context.

        Returns:
            Tuple of (intent_category, confidence_score).
            Intent is one of: registration, deadlines, voting_methods,
            requirements, polling_locations, candidates, general.
        """
        client = self._get_client()

        prompt = (
            "Classify the user's election-related question into one of these categories:\n"
            "- registration: Questions about registering to vote\n"
            "- deadlines: Questions about election dates and deadlines\n"
            "- voting_methods: Questions about how to vote (mail, early, in-person)\n"
            "- requirements: Questions about voter ID, eligibility, documents\n"
            "- polling_locations: Questions about where to vote\n"
            "- candidates: Questions about candidates or ballot measures\n"
            "- general: Other election-related questions\n\n"
            "Conversation Context: %s\n"
            'Message: "%s"\n\n'
            'Output ONLY JSON: {"intent": "category", "confidence": 0.0-1.0}'
        ) % (context, message)

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
            logger.warning("Intent classification failed: %s", e)
            return "general", 0.5

    def generate_response(self, message: str, intent: str, context: dict, conversation_context: str = "") -> str:
        """Generate a helpful, non-partisan response.

        Args:
            message: User's original question.
            intent: Classified intent category.
            context: Relevant context information for the intent.
            conversation_context: Previous conversation history.

        Returns:
            Generated response text, or fallback response on error.
        """
        client = self._get_client()

        prompt = (
            "You are a helpful, non-partisan election assistant. "
            "Provide clear, accurate information.\n\n"
            "Conversation Context: %s\n"
            "User Question: %s\n"
            "Intent Category: %s\n"
            "Available Information: %s\n\n"
            "Guidelines:\n"
            "1. Be factual and unbiased\n"
            "2. Note when rules vary by state\n"
            "3. Suggest specific next steps\n"
            "4. Keep response conversational but informative\n"
            "5. Do not express political opinions\n"
            "6. Use the conversation context to provide more specific, "
            "follow-up answers\n\n"
            "Generate a helpful response:"
        ) % (conversation_context, message, intent, json.dumps(context))

        try:
            response = client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Broad catch because Gemini library may raise various exceptions (network, auth, quota, etc.)
            logger.error("Response generation failed: %s", e)
            return self._get_fallback_response(intent)

    async def understand_intent_async(self, message: str, context: str = "") -> Tuple[str, float]:
        """Async wrapper for intent classification with timeout.

        Args:
            message: User's question text.
            context: Previous conversation context.

        Returns:
            Tuple of (intent_category, confidence_score).
        """
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self.understand_intent, message, context),
                timeout=LLM_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.warning("Gemini intent classification timed out after %ds", LLM_TIMEOUT)
            return "general", 0.5

    async def generate_response_async(self, message: str, intent: str, context: dict, conversation_context: str = "") -> str:
        """Async wrapper for response generation with timeout.

        Args:
            message: User's original question.
            intent: Classified intent category.
            context: Relevant context information for the intent.
            conversation_context: Previous conversation history.

        Returns:
            Generated response text, or fallback response on error/timeout.
        """
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self.generate_response, message, intent, context, conversation_context),
                timeout=LLM_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.warning("Gemini response generation timed out after %ds", LLM_TIMEOUT)
            return self._get_fallback_response(intent)

    def _get_fallback_response(self, intent: str) -> str:
        """Provide a fallback response when Gemini is unavailable.

        Args:
            intent: The classified intent category.

        Returns:
            Pre-written fallback response string.
        """
        fallbacks = {
            "registration": "To register to vote, check your state's election website. Most states offer online registration. You'll need to be a US citizen, state resident, and at least 18 years old by Election Day.",
            "deadlines": "Election deadlines vary by state. Key dates include voter registration deadlines (typically 15-30 days before Election Day), early voting periods, and mail ballot request deadlines.",
            "voting_methods": "You can vote in person on Election Day, vote early at designated locations, or vote by mail. Check your state's options.",
            "requirements": "Voter ID requirements vary by state. Some require photo ID, others accept non-photo ID or no ID. First-time voters may need additional documentation.",
            "polling_locations": "Find your polling place on your voter registration card or your state's election website. Hours are typically 7 AM to 7 PM.",
            "candidates": "Check your state's official election website for a sample ballot showing all candidates and measures.",
            "general": "I can help with voter registration, election deadlines, voting methods, ID requirements, and finding your polling place. What would you like to know?",
        }
        return fallbacks.get(intent, fallbacks["general"])
