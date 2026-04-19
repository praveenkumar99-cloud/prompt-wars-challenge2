import pytest
from unittest.mock import patch, AsyncMock
from gmail_watcher import GmailWatcher
import httpx

@pytest.mark.asyncio
async def test_prompt_output_structure():
    """Verify Prompt extraction correctly populates structured Pydantic architecture."""
    with patch("gmail_watcher.genai.GenerativeModel") as mock_model_class:
        mock_model = AsyncMock()
        mock_model.generate_content_async.return_value.text = "{}"
        mock_model_class.return_value = mock_model
        
        async with httpx.AsyncClient() as client:
            watcher = GmailWatcher(client)
            result = await watcher._call_gemini("Action required: Submit Q3 report by Friday")
            
            assert isinstance(result, dict)
            assert "title" in result
            assert "urgency_score" in result
            assert "importance_score" in result
            assert result["category"] == "Work"
            assert result["source"] == "gmail"

@pytest.mark.asyncio
async def test_model_routing_logic():
    """Verify Gemini Model switches between flash and pro effectively based on snippet length natively."""
    with patch("gmail_watcher.genai.GenerativeModel") as mock_model_class:
        mock_model = AsyncMock()
        mock_model_class.return_value = mock_model
        
        async with httpx.AsyncClient() as client:
            watcher = GmailWatcher(client)
            
            # Short Snippet routes to Flash naturally
            await watcher._call_gemini("short text " * 5)
            mock_model_class.assert_called_with("gemini-1.5-flash")
            
            # Long Snippet routes to Context-Heavy Pro
            long_text = "a" * 250
            await watcher._call_gemini(long_text)
            mock_model_class.assert_called_with("gemini-1.5-pro")
