from fastapi.testclient import TestClient

from app.server import create_app


client = TestClient(create_app())


def test_chat_endpoint_rejects_empty_message():
    response = client.post("/api/chat", json={"message": "   ", "session_id": "test"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Message cannot be empty"


def test_chat_endpoint_returns_structured_response():
    response = client.post("/api/chat", json={"message": "How do I register to vote?", "session_id": "test"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "registration"
    assert isinstance(payload["follow_up_suggestions"], list)
    assert isinstance(payload["sources"], list)


def test_timeline_endpoint_returns_expected_shape():
    response = client.get("/api/timeline")

    assert response.status_code == 200
    payload = response.json()
    assert payload["election_year"] == 2024
    assert isinstance(payload["events"], list)
    assert "deadlines" in payload


def test_steps_endpoint_returns_known_step():
    response = client.get("/api/steps/register")

    assert response.status_code == 200
    payload = response.json()
    assert payload["step_id"] == "register"
    assert len(payload["actions"]) > 0


def test_steps_endpoint_returns_not_found_for_unknown_step():
    response = client.get("/api/steps/unknown-step")

    assert response.status_code == 404
