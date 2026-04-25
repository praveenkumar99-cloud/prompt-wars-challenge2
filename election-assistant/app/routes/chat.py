"""Module: chat.py
Description: Chat endpoint for election assistant.
Author: Praveen Kumar
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ..constants import MAX_MESSAGE_LENGTH
from ..models import ChatRequest, ChatResponse
from ..services.assistant_service import AssistantService

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)


def get_assistant_service() -> AssistantService:
    """Dependency injection provider for AssistantService.

    Returns:
        AssistantService instance.
    """
    return AssistantService()


def get_assistant_service() -> AssistantService:
    """Dependency injection provider for AssistantService.

    Returns:
        AssistantService instance.
    """
    return AssistantService()


@router.post(
    "/chat",
    status_code=200,
    response_model=ChatResponse,
    tags=["chat"],
    summary="Send a message to the election assistant",
)
async def chat(
    request: ChatRequest, service: AssistantService = Depends(get_assistant_service)
) -> ChatResponse:
    """Send a message to the election assistant and get a response.

    **Request Body:**
        - message: User's question (1-500 characters)
        - session_id: Optional session identifier

    **Response:**
        - response: Assistant's response message
        - intent: Classified intent category
        - follow_up_suggestions: List of suggested follow-up questions
        - sources: List of information sources

    **Error Responses:**
        - 400: Message is empty or exceeds 500 characters
        - 500: Internal server error
    """
    try:
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(400, "Message cannot be empty")

        if len(request.message) > MAX_MESSAGE_LENGTH:
            raise HTTPException(400, "Message too long, max 500 characters")

        result = await service.process_message(
            request.message,
            request.session_id,
        )
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Chat error: %s", exc)
        raise HTTPException(500, "Internal server error") from exc
