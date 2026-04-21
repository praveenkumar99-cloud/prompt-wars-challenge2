"""Election timeline information service"""
import json
import os
from datetime import datetime
from typing import List, Dict
from ..models import TimelineEvent

class TimelineService:
    """Service for providing election timeline information"""
    
    def __init__(self):
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """Load election knowledge data"""
        knowledge_path = os.path.join(os.path.dirname(__file__), "..", "data", "election_knowledge.json")
        try:
            with open(knowledge_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    
    def get_full_timeline(self) -> List[Dict]:
        """Get complete election timeline"""
        return self.knowledge.get("important_dates_2024", [])
    
    def get_upcoming_events(self, days_ahead: int = 30) -> List[Dict]:
        """Get events within specified days (mock implementation)"""
        all_events = self.get_full_timeline()
        # In production, this would calculate actual dates
        return all_events[:3]  # Return first 3 as "upcoming" for demo
    
    def get_event_by_name(self, event_name: str) -> Dict:
        """Get specific event details"""
        for event in self.get_full_timeline():
            if event_name.lower() in event.get("event", "").lower():
                return event
        return None
    
    def get_deadline_info(self) -> Dict:
        """Get voter registration deadline information"""
        return {
            "registration_deadline": self.knowledge.get("registration", {}).get("deadline", "Varies by state"),
            "mail_ballot_deadline": "Typically 7-15 days before Election Day",
            "early_voting_period": "Typically 2-4 weeks before Election Day"
        }
