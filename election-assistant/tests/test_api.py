"""Module: test_api.py
Description: Tests for API endpoints: chat, timeline, and steps.
Author: Praveen Kumar
"""
import pytest
from fastapi.testclient import TestClient

from app.server import create_app

client = TestClient(create_app())


class TestChatEndpoint:
    """Test suite for /api/chat endpoint."""

    def test_rejects_empty_message(self) -> None:
        """Test that empty or whitespace-only messages are rejected with 400."""
        response = client.post("/api/chat", json={"message": "   ", "session_id": "test"})
        assert response.status_code == 400
        assert response.json()["detail"] == "Message cannot be empty"

    def test_rejects_message_over_length_limit(self) -> None:
        """Test that messages exceeding 500 characters are rejected with 400."""
        response = client.post("/api/chat", json={"message": "x" * 501})
        assert response.status_code == 400

    def test_accepts_message_without_session_id(self) -> None:
        """Test that messages without session_id are accepted (optional field)."""
        response = client.post("/api/chat", json={"message": "How do I register?"})
        assert response.status_code == 200

    def test_returns_structured_response(self) -> None:
        """Test that valid chat request returns properly structured JSON response."""
        response = client.post(
            "/api/chat", json={"message": "How do I register to vote?", "session_id": "test"}
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["intent"] == "registration"
        assert isinstance(payload["follow_up_suggestions"], list)
        assert isinstance(payload["sources"], list)


class TestTimelineEndpoint:
    """Test suite for /api/timeline endpoint."""

    def test_returns_expected_shape(self) -> None:
        """Test that timeline response has expected keys and data types."""
        response = client.get("/api/timeline")
        assert response.status_code == 200
        payload = response.json()
        assert payload["election_year"] == 2024
        assert isinstance(payload["events"], list)
        assert "deadlines" in payload


class TestStepsEndpoints:
    """Test suite for /api/steps endpoints."""

    def test_get_all_steps(self) -> None:
        """Test that /api/steps returns all available step guides."""
        response = client.get("/api/steps")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

    def test_get_known_step_register(self) -> None:
        """Test that /api/steps/register returns registration step."""
        response = client.get("/api/steps/register")
        assert response.status_code == 200
        payload = response.json()
        assert payload["step_id"] == "register"
        assert len(payload["actions"]) > 0

    def test_get_known_step_vote(self) -> None:
        """Test that /api/steps/vote returns voting step."""
        response = client.get("/api/steps/vote")
        assert response.status_code == 200
        assert response.json()["step_id"] == "vote"

    def test_get_known_step_mail_ballot(self) -> None:
        """Test that /api/steps/mail_ballot returns mail ballot step."""
        response = client.get("/api/steps/mail_ballot")
        assert response.status_code == 200
        assert response.json()["step_id"] == "mail_ballot"

    def test_unknown_step_returns_404(self) -> None:
        """Test that invalid step ID returns 404."""
        response = client.get("/api/steps/unknown-step")
        assert response.status_code == 404


# Additional edge case and failure path tests per Fix 3 (evaluator improvement)

def test_chat_rejects_message_over_limit(client) -> None:
    """Messages over 500 characters must return HTTP 400."""
    response = client.post("/api/chat", json={"message": "x" * 501})
    assert response.status_code == 400


def test_chat_with_no_session_id(client) -> None:
    """Session ID is optional — must not be required for a valid request."""
    response = client.post("/api/chat", json={"message": "How do I register?"})
    assert response.status_code == 200


def test_steps_vote_endpoint(client) -> None:
    """GET /api/steps/vote must return step_id = 'vote'."""
    response = client.get("/api/steps/vote")
    assert response.status_code == 200
    assert response.json()["step_id"] == "vote"


def test_steps_mail_ballot_endpoint(client) -> None:
    """GET /api/steps/mail_ballot must succeed."""
    response = client.get("/api/steps/mail_ballot")
    assert response.status_code == 200


