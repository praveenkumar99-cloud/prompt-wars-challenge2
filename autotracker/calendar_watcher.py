"""
Calendar Watcher Module - Buildathon Edition.
Uses native httpx for REST parsing and TypedDict for strict typing globally shared.
"""
from typing import List, Dict, Any, TypedDict, Optional
from datetime import datetime, timedelta
import httpx
import google.auth
import google.auth.transport.requests

from utils import logger, cache_results, resilient_api_call

class EventItem(TypedDict, total=False):
    id: str
    summary: str
    description: str
    start: Dict[str, str]
    attachments: List[Any]

class CalendarResponse(TypedDict):
    items: List[EventItem]

class CalendarWatcher:
    """Monitors Google Calendar REST API strictly through shared Context."""
    
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.headers = {}
        
    async def initialize(self) -> None:
        """Asynchronously initialize credential payloads."""
        logger.info("Initializing CalendarWatcher bindings async.")
        credentials, _ = google.auth.default()
        req = google.auth.transport.requests.Request()
        credentials.refresh(req)
        self.headers = {"Authorization": f"Bearer {credentials.token}"}
        
    @cache_results(maxsize=50)
    def _needs_preparation(self, event_description: Optional[str], event_attachments: Optional[List[Any]]) -> bool:
        """Check if an event requires preparation."""
        return bool(event_attachments or event_description)

    @resilient_api_call()
    async def fetch_upcoming_events(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Fetch using raw httpx and circuit breaking."""
        now = datetime.utcnow().isoformat() + 'Z'
        later = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
        url = f"https://www.googleapis.com/calendar/v3/calendars/primary/events"
        params = {
            "timeMin": now,
            "timeMax": later,
            "singleEvents": "true",
            "orderBy": "startTime"
        }
        
        response = await self.client.get(url, headers=self.headers, params=params, timeout=10.0)
        response.raise_for_status()
        data: CalendarResponse = response.json()
        
        tasks = []
        for event in data.get('items', []):
            if self._needs_preparation(event.get('description'), event.get('attachments')):
                tasks.append({
                    'title': f"Prepare for: {event.get('summary', 'Untitled Event')}",
                    'deadline': event.get('start', {}).get('dateTime'),
                    'urgency_score': 60,
                    'importance_score': 60,
                    'effort_score': 30,
                    'category': "Work",
                    'source': 'calendar',
                    'event_id': event.get('id')
                })
        return tasks
