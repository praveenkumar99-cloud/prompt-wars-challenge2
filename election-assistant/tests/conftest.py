"""Module: conftest
Description: Shared pytest fixtures for all test modules.
Author: Praveen Kumar
"""
import pytest
from fastapi.testclient import TestClient

from app.server import create_app


@pytest.fixture(scope="module")
def client():
    """Shared FastAPI test client for all endpoint tests."""
    return TestClient(create_app())


@pytest.fixture
def sample_chat_payload():
    """Standard chat request payload for reuse across tests."""
    return {"message": "How do I register to vote?", "session_id": "test-123"}


@pytest.fixture
def long_message_payload():
    """Oversized message payload for boundary testing."""
    return {"message": "x" * 501}
