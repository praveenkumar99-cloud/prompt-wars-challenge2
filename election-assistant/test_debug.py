#!/usr/bin/env python
"""Debug script to test the chat endpoint"""
import sys
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.server import create_app

client = TestClient(create_app())

response = client.post("/api/chat", json={"message": "How do I register?"})
print("Status:", response.status_code)
print("Response:", response.text[:500])
