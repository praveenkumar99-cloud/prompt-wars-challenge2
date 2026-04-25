"""Module: test_intent.py
Description: Tests for the IntentService classification and suggestions.
Author: Praveen Kumar
"""
from app.services.intent_service import IntentService


class TestIntentService:
    """Test suite for IntentService functionality."""

    def test_keyword_classification(self) -> None:
        """Test that keyword-based classification correctly identifies intents."""
        service = IntentService()
        # Without API key, fallback keyword classification is used
        intent = service._keyword_classify("How do I register to vote?")
        assert intent == "registration"

        intent = service._keyword_classify("When is the deadline to vote by mail?")
        assert intent == "deadlines"

        intent = service._keyword_classify("Where is my polling location?")
        assert intent == "polling_locations"

    def test_suggestions_for_intents(self) -> None:
        """Test that follow-up suggestions are returned for each intent."""
        service = IntentService()
        for intent in [
            "registration",
            "deadlines",
            "voting_methods",
            "requirements",
            "polling_locations",
            "candidates",
            "general",
        ]:
            suggestions = service.get_follow_up_suggestions(intent)
            assert len(suggestions) > 0
            # Verify suggestions are strings
            assert all(isinstance(s, str) for s in suggestions)
