import pytest
from unittest.mock import patch, MagicMock

from gmail_watcher import GmailWatcher
from drive_watcher import DriveWatcher
from calendar_watcher import CalendarWatcher

@pytest.fixture
def mock_google_auth():
    with patch("google.auth.default", return_value=(MagicMock(), "test-project")):
        yield

@pytest.mark.asyncio
async def test_calendar_watcher(mock_google_auth):
    with patch("calendar_watcher.build") as mock_build:
        watcher = CalendarWatcher()
        mock_events = mock_build.return_value.events.return_value.list.return_value.execute
        mock_events.return_value = {
            "items": [
                {
                    "id": "123",
                    "summary": "Important Meeting",
                    "description": "Prepare slides",
                    "start": {"dateTime": "2026-04-19T10:00:00Z"}
                }
            ]
        }
        
        tasks = await watcher.fetch_upcoming_events()
        assert len(tasks) == 1
        assert "Prepare for:" in tasks[0]["title"]
        assert tasks[0]["source"] == "calendar"

@pytest.mark.asyncio
async def test_drive_watcher(mock_google_auth):
    with patch("drive_watcher.build") as mock_build:
        watcher = DriveWatcher()
        mock_files = mock_build.return_value.files.return_value.list.return_value.execute
        mock_files.return_value = {
            "files": [
                {
                    "id": "abc",
                    "name": "Design Doc",
                    "lastModifyingUser": {"emailAddress": "colleague@example.com"}
                }
            ]
        }
        
        tasks = await watcher.fetch_recent_changes()
        assert len(tasks) == 1
        assert "Review changes" in tasks[0]["title"]
        assert tasks[0]["source"] == "drive"
