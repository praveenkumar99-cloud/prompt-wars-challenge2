"""Module: test_assistant
Description: Tests for AssistantService including fallback behavior,
             Gemini failure paths, and edge case handling.
Author: Praveen Kumar
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.assistant_service import AssistantService
from app.services.gemini_service import GeminiService


class TestAssistantFallbackBehavior:
    """Tests for fallback behavior when Gemini API is unavailable."""

    @pytest.mark.asyncio
    async def test_process_message_returns_required_keys(self):
        """All required response keys must be present in every response."""
        service = AssistantService()
        result = await service.process_message("How do I vote by mail?", "test-session")
        assert "response" in result
        assert "intent" in result
        assert "follow_up_suggestions" in result
        assert "sources" in result

    @pytest.mark.asyncio
    async def test_voting_methods_intent_detected(self):
        """'Vote by mail' phrasing must resolve to voting_methods intent."""
        service = AssistantService()
        result = await service.process_message("How do I vote by mail?", "test-session")
        assert result["intent"] == "voting_methods"
        assert len(result["follow_up_suggestions"]) > 0

    @pytest.mark.asyncio
    async def test_gemini_exception_does_not_crash(self):
        """Gemini API errors must return a graceful fallback, not raise."""
        with patch(
            "app.services.gemini_service.GeminiService.generate_response",
            side_effect=Exception("API unavailable")
        ):
            service = AssistantService()
            result = await service.process_message("How do I register?", "sess-err")
            assert "response" in result
            assert isinstance(result["response"], str)
            assert len(result["response"]) > 0

    @pytest.mark.asyncio
    async def test_empty_session_id_handled(self):
        """None session_id must not crash the service."""
        service = AssistantService()
        result = await service.process_message("When is election day?", None)
        assert "response" in result


class TestGeminiFallbackIntents:
    """Tests for GeminiService fallback response coverage."""

    def test_all_intents_have_fallback(self):
        """Every intent must return a non-empty fallback string."""
        svc = GeminiService()
        intents = [
            "registration", "deadlines", "voting_methods",
            "requirements", "polling_locations", "candidates", "general"
        ]
        for intent in intents:
            resp = svc._get_fallback_response(intent)
            assert isinstance(resp, str), f"Fallback for '{intent}' is not a string"
            assert len(resp) > 10, f"Fallback for '{intent}' is too short"

    def test_malformed_gemini_json_returns_general_intent(self):
        """When Gemini returns unparseable JSON, intent must default to 'general'."""
        svc = GeminiService()
        with patch.object(svc, "_get_client") as mock_client:
            mock_client.return_value.generate_content.return_value.text = (
                "not valid json {{{"
            )
            intent, confidence = svc.understand_intent("random question")
            assert intent == "general"
            assert confidence == 0.5

    def test_empty_gemini_response_handled(self):
        """Empty Gemini response must not raise an exception."""
        svc = GeminiService()
        with patch.object(svc, "_get_client") as mock_client:
            mock_client.return_value.generate_content.return_value.text = ""
            intent, confidence = svc.understand_intent("anything")
            assert isinstance(intent, str)
