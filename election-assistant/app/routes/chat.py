"""Chat endpoint for election assistant."""
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..models import ChatRequest
from ..services.assistant_service import AssistantService

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)

assistant_service = AssistantService()


@router.post("/chat")
async def chat(request: ChatRequest):
    """Send a message to the election assistant."""
    try:
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(400, "Message cannot be empty")

        result = await assistant_service.process_message(
            request.message,
            request.session_id,
        )
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Chat error: %s", exc)
        raise HTTPException(500, "Internal server error")
