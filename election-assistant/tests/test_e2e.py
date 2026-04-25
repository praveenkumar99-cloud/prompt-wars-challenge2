from fastapi.testclient import TestClient

from app.server import create_app


client = TestClient(create_app())


def test_root_page_loads():
    response = client.get("/")

    assert response.status_code == 200
    assert "Election Process Assistant" in response.text
    assert 'id="chat-messages"' in response.text


def test_system_status_endpoint():
    response = client.get("/api/system/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project_id"] == "praveen-space"
    assert "google_api_key_configured" in payload
