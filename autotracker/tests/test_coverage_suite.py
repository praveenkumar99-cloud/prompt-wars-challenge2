import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock

from utils import get_secret_async
from gmail_watcher import GmailWatcher

@pytest.mark.asyncio
async def test_secret_manager_async_mock():
    """Verify SecretManagerServiceAsyncClient is mocked successfully natively across async thresholds."""
    with patch("utils.secretmanager_v1.SecretManagerServiceAsyncClient") as mock_client_class:
        mock_instance = AsyncMock()
        mock_instance.access_secret_version.return_value.payload.data.decode.return_value = "mock_secret_123"
        mock_client_class.return_value = mock_instance
        
        secret = await get_secret_async("test_key")
        assert secret == "mock_secret_123"

@pytest.mark.asyncio
async def test_gemini_retry_exponential_backoff():
    """Verify Gemini API retries correctly via decorator under explicit 429/500 errors."""
    with patch("gmail_watcher.genai.GenerativeModel") as mock_model_class:
        mock_model = MagicMock()
        
        # Raise an exception exactly 3 times before succeeding simulating network recovery!
        mock_model.generate_content_async = AsyncMock(side_effect=[
            Exception("500 Internal Server Error"),
            Exception("429 Too Many Requests"),
            Exception("503 Service Unavailable"),
            MagicMock(text="{}") # Succeeds on the 4th attempt
        ])
        mock_model_class.return_value = mock_model
        
        async with httpx.AsyncClient() as client:
            watcher = GmailWatcher(client)
            
            result = await watcher._call_gemini("test snippet")
            
            # Assert tenacity correctly iterated through failure layers specifically
            assert mock_model.generate_content_async.call_count == 4
            assert isinstance(result, dict)
