import pytest
from fastapi.testclient import TestClient
from app.server import app

client = TestClient(app)

def test_end_to_end():
    # Step 1: Google Sign-In
    response = client.post("/auth/google-signin", json={"id_token": "test-token"})
    assert response.status_code == 200

    # Step 2: Ask a question
    response = client.post("/vertex-ai/gemini", json={"query": "What are the election dates?"})
    assert response.status_code == 200
    assert "response" in response.json()

    # Step 3: Download guide
    response = client.get("/download/guide/sample-guide-id")
    assert response.status_code == 200
    assert "download_url" in response.json()