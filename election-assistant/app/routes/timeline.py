"""Module: timeline.py
Description: Timeline endpoint for election dates.
Author: Praveen Kumar
"""
from fastapi import APIRouter, Depends

from ..config import config
from ..models import TimelineResponse
from ..services.timeline_service import TimelineService

router = APIRouter(prefix="/api", tags=["timeline"])


def get_timeline_service() -> TimelineService:
    """Dependency injection provider for TimelineService.

    Returns:
        TimelineService instance.
    """
    return TimelineService()


@router.get(
    "/timeline",
    response_model=TimelineResponse,
    status_code=200,
    tags=["timeline"],
    summary="Get election timeline and key dates",
)
async def get_timeline(
    service: TimelineService = Depends(get_timeline_service),
) -> TimelineResponse:
    """Get complete election timeline information.

    **Response:**
        - election_year: The election year (2024)
        - events: Complete list of election events
        - upcoming: Upcoming events within the next 30 days
        - deadlines: Key deadline information
    """
    return {
        "election_year": config.ELECTION_YEAR,
        "events": service.get_full_timeline(),
        "upcoming": service.get_upcoming_events(),
        "deadlines": service.get_deadline_info(),
    }
