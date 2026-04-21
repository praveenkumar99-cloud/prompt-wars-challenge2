"""Timeline endpoint for election dates"""
from fastapi import APIRouter
from ..services.timeline_service import TimelineService

router = APIRouter(prefix="/api", tags=["timeline"])
timeline_service = TimelineService()

@router.get("/timeline")
async def get_timeline():
    """Get complete election timeline"""
    return {
        "election_year": 2024,
        "events": timeline_service.get_full_timeline(),
        "upcoming": timeline_service.get_upcoming_events(),
        "deadlines": timeline_service.get_deadline_info()
    }
