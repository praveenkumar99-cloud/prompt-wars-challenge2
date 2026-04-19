from google.auth import default
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict

class CalendarWatcher:
    """Monitors Google Calendar for upcoming events requiring preparation"""
    
    def __init__(self):
        credentials, project = default()
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def fetch_upcoming_events(self, days_ahead: int = 7) -> List[Dict]:
        """Fetch upcoming events and identify prep needs"""
        now = datetime.utcnow().isoformat() + 'Z'
        later = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        events = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=later,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        tasks = []
        for event in events.get('items', []):
            if self._needs_preparation(event):
                tasks.append({
                    'title': f"Prepare for: {event['summary']}",
                    'deadline': event['start']['dateTime'],
                    'source': 'calendar',
                    'event_id': event['id']
                })
        return tasks
    
    def _needs_preparation(self, event: Dict) -> bool:
        """Check if event has attachments or requires prep"""
        return 'attachments' in event or 'description' in event
