"""Module: timeline_service.py
Description: Election timeline information service.
Author: Praveen Kumar
"""
__all__ = ["TimelineService"]

import json
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class TimelineService:
    """Service for providing election timeline information."""

    def __init__(self) -> None:
        """Initialize TimelineService by loading election knowledge data."""
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self) -> Dict[str, Any]:
        """Load election knowledge data from JSON file.

        Returns:
            Dictionary containing election data, or empty dict on error.
        """
        knowledge_path = os.path.join(os.path.dirname(__file__), "..", "data", "election_knowledge.json")
        try:
            with open(knowledge_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            logger.error("Election knowledge file not found: %s", e)
            return {}
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in election knowledge file: %s", e)
            return {}

    def get_full_timeline(self) -> List[Dict[str, Any]]:
        """Get complete election timeline.

        Returns:
            List of election event dictionaries.
        """
        raw_events = self.knowledge.get("important_dates_2024", [])
        formatted_events = []
        for i, event in enumerate(raw_events):
            formatted_events.append({
                "event_id": f"event_{i+1}",
                "title": event.get("event", ""),
                "date": event.get("date") or event.get("date_range", ""),
                "description": event.get("description", ""),
                "is_deadline": "deadline" in event.get("event", "").lower() or "registration" in event.get("event", "").lower()
            })
        return formatted_events

    def get_upcoming_events(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get the nearest election events.

        Args:
            days_ahead: Number of days to look ahead (kept for API compatibility).

        Returns:
            List of upcoming event dictionaries (max 3 items).
        """
        all_events = self.get_full_timeline()
        # Return up to 3 nearest events
        return all_events[: min(3, len(all_events))]

    def get_deadline_info(self) -> Dict[str, str]:
        """Get voter registration deadline information.

        Returns:
            Dictionary with deadline information for registration, mail ballot, and early voting.
        """
        return {
            "registration_deadline": self.knowledge.get("registration", {}).get(
                "deadline", "Varies by state"
            ),
            "mail_ballot_deadline": "Typically 7-15 days before Election Day",
            "early_voting_period": "Typically 2-4 weeks before Election Day",
        }
