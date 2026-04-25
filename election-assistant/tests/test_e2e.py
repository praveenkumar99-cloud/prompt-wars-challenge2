"""Module: test_e2e.py
Description: End-to-end tests for the Election Assistant application.
Author: Praveen Kumar
"""
from fastapi.testclient import TestClient

from app.server import create_app


client = TestClient(create_app())


class TestE2EFlow:
    """Test suite for end-to-end application behavior."""

    def test_root_page_loads(self) -> None:
        """Test that the root endpoint returns the HTML chat interface."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Election Process Assistant" in response.text
        assert 'id="chat-messages"' in response.text

    def test_system_status_endpoint(self) -> None:
        """Test that system status returns expected configuration fields."""
        response = client.get("/api/system/status")
        assert response.status_code == 200
        payload = response.json()
        assert payload["project_id"] == "praveen-space"
        assert "google_api_key_configured" in payload
