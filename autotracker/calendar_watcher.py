"""
Calendar Watcher Module.

This module provides a watcher that monitors Google Calendar for upcoming events
requiring preparation or attention.
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
from google.auth import default
from googleapiclient.discovery import build

from utils import logger, cache_results

class CalendarWatcher:
    """
    Monitors Google Calendar for upcoming events requiring preparation.
    """
    
    def __init__(self) -> None:
        """Initializes the Calendar API client."""
        logger.info("Initializing CalendarWatcher")
        credentials, project = default()
        self.service = build('calendar', 'v3', credentials=credentials)
    
    @cache_results(maxsize=50)
    def _needs_preparation(self, event: Dict[str, Any]) -> bool:
        """
        Check if an event has attachments or requires preparation based on description.
        
        Args:
            event (Dict[str, Any]): The calendar event.
            
        Returns:
            bool: True if it needs preparation, False otherwise.
        """
        return 'attachments' in event or 'description' in event

    async def fetch_upcoming_events(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch upcoming events and identify preparation needs asynchronously.
        
        Args:
            days_ahead (int): Number of days to look ahead. Defaults to 7.
            
        Returns:
            List[Dict[str, Any]]: A list of task dictionaries derived from events.
        """
        logger.info(f"Fetching upcoming calendar events for the next {days_ahead} days")
        now = datetime.utcnow().isoformat() + 'Z'
        later = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
        
        try:
            events_result = await asyncio.to_thread(
                self.service.events().list(
                    calendarId='primary',
                    timeMin=now,
                    timeMax=later,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute
            )
            
            tasks = []
            for event in events_result.get('items', []):
                if self._needs_preparation(event):
                    tasks.append({
                        'title': f"Prepare for: {event.get('summary', 'Untitled Event')}",
                        'deadline': event.get('start', {}).get('dateTime'),
                        'urgency_score': 60,
                        'importance_score': 60,
                        'effort_score': 30,
                        'category': "Work",
                        'source': 'calendar',
                        'event_id': event['id']
                    })
            
            logger.info(f"Extracted {len(tasks)} tasks from Calendar.")
            return tasks
        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return []
