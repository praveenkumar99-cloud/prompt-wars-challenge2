"""Module: test_timeline.py
Description: Tests for the TimelineService data loading and queries.
Author: Praveen Kumar
"""
from app.services.timeline_service import TimelineService


class TestTimelineService:
    """Test suite for TimelineService functionality."""

    def test_loads_timeline_successfully(self) -> None:
        """Test that election timeline data loads from JSON file."""
        service = TimelineService()
        timeline = service.get_full_timeline()
        assert isinstance(timeline, list)

    def test_upcoming_events_limited_to_three(self) -> None:
        """Test that upcoming events returns at most 3 items and first is primary."""
        service = TimelineService()
        upcoming = service.get_upcoming_events()
        assert len(upcoming) <= 3
        if upcoming:
            assert upcoming[0]["title"] == "Primary Elections"

    def test_deadline_info_structure(self) -> None:
        """Test that deadline info contains required keys."""
        service = TimelineService()
        deadlines = service.get_deadline_info()
        assert "registration_deadline" in deadlines
        assert "mail_ballot_deadline" in deadlines
        assert "early_voting_period" in deadlines
