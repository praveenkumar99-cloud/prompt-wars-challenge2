import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app

client = TestClient(app)

@patch("main.TaskGenerator.generate_tasks", new_callable=AsyncMock)
def test_get_tasks(mock_generate):
    mock_generate.return_value = [
        {
             "title": "Mocked Task",
             "urgency_score": 80,
             "importance_score": 70,
             "effort_score": 50,
             "category": "Work",
             "source": "gmail",
             "priority": 71.0
        }
    ]
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Mocked Task"

def test_refresh_tasks():
    response = client.post("/api/refresh")
    assert response.status_code == 200
    assert response.json() == {"status": "processing"}
