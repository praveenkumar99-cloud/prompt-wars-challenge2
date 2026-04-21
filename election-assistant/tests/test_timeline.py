import pytest
from app.services.timeline_service import TimelineService

def test_timeline_load():
    service = TimelineService()
    timeline = service.get_full_timeline()
    assert isinstance(timeline, list)
    
def test_timeline_upcoming():
    service = TimelineService()
    upcoming = service.get_upcoming_events()
    assert len(upcoming) <= 3
    assert upcoming[0]["event"] == "Primary Elections"
    
def test_deadlines():
    service = TimelineService()
    deadlines = service.get_deadline_info()
    assert "registration_deadline" in deadlines
    assert "mail_ballot_deadline" in deadlines
