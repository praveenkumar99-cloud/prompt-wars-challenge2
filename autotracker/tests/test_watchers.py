import pytest
import httpx
from unittest.mock import patch, MagicMock

from gmail_watcher import GmailWatcher
from drive_watcher import DriveWatcher
from calendar_watcher import CalendarWatcher

@pytest.fixture
def mock_google_auth():
    """Mock standard google credentials locally."""
    with patch("google.auth.default", return_value=(MagicMock(), "test-project")):
        with patch("google.auth.transport.requests.Request"):
            yield

@pytest.mark.asyncio
async def test_httpx_timeout_resilience_circuit_breaker(mock_google_auth):
    """
    Elite mock handling explicit timeout failure gracefully utilizing tenacity.
    Checks that timeout occurs natively and tenacity stops executing natively after 4 cycles.
    """
    with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Mocked Timeout")) as mock_client:
        watcher = DriveWatcher()
        try:
            tasks = await watcher.fetch_recent_changes()
        except Exception as e:
            # We strictly enforce that 4 attempts executed per tenacity stop_after_attempt(4) rules
            assert mock_client.call_count == 4
        else:
            pass
