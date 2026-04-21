import pytest
import asyncio
from app.services.assistant_service import AssistantService

@pytest.mark.asyncio
async def test_assistant_process_message_fallback():
    # Tests the fallback behavior (assumes GOOGLE_API_KEY is not set or valid in test env)
    service = AssistantService()
    result = await service.process_message("How do I vote by mail?", "test-session")
    
    assert "response" in result
    assert "intent" in result
    assert "follow_up_suggestions" in result
    assert "sources" in result
    
    # "vote by mail" triggers voting_methods
    assert result["intent"] == "voting_methods"
    assert len(result["follow_up_suggestions"]) > 0
