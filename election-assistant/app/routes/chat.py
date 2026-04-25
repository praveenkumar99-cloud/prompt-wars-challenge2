"""Module: chat.py
Description: Chat endpoint for election assistant with input validation and security.
Author: Praveen Kumar
"""
import hashlib
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..constants import (
    HTTP_STATUS_BAD_REQUEST,
    HTTP_STATUS_INTERNAL_SERVER_ERROR,
    LOG_INTENT_CLASSIFICATION_FAILED,
    LOG_RESPONSE_GENERATION_FAILED,
    MAX_MESSAGE_LENGTH,
)
from ..models import ChatRequest, ChatResponse
from ..services.assistant_service import AssistantService
from ..services.audit_service import AuditService
from ..services.cache_service import CacheService
from ..utils.input_sanitizer import InputSanitizer

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)

# Rate limiter: 100 requests per minute per IP
limiter = Limiter(key_func=get_remote_address)


def get_assistant_service() -> AssistantService:
    """Dependency injection provider for AssistantService.

    Returns:
        AssistantService instance.
    """
    return AssistantService()


def get_audit_service() -> AuditService:
    """Dependency injection provider for AuditService.

    Returns:
        AuditService instance.
    """
    return AuditService()


def get_cache_service() -> CacheService:
    """Dependency injection provider for CacheService.

    Returns:
        CacheService instance.
    """
    return CacheService()


@router.post(
    "/chat",
    status_code=200,
    response_model=ChatResponse,
    tags=["chat"],
    summary="Send a message to the election assistant",
)
@limiter.limit("100/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    service: AssistantService = Depends(get_assistant_service),
    audit_service: AuditService = Depends(get_audit_service),
    cache_service: CacheService = Depends(get_cache_service),
) -> ChatResponse:
    """Send a message to the election assistant and get a response.

    **Request Body:**
        - message: User's question (1-500 characters)
        - session_id: Optional session identifier
        - language: Optional language code (en/es)

    **Response:**
        - response: Assistant's response message
        - intent: Classified intent category
        - follow_up_suggestions: List of suggested follow-up questions
        - sources: List of information sources
        - session_id: Session identifier for tracking

    **Error Responses:**
        - 400: Message is empty or exceeds 500 characters
        - 429: Rate limit exceeded (100 requests/minute)
        - 500: Internal server error

    Args:
        request: HTTP request.
        chat_request: Chat request payload.
        service: AssistantService instance.
        audit_service: AuditService instance.
        cache_service: CacheService instance.

    Returns:
        ChatResponse with assistant's answer.

    Raises:
        HTTPException: For validation or processing errors.
    """
    user_ip: str = request.client.host if request.client else "unknown"
    session_id: str = chat_request.session_id or "anonymous"

    try:
        # Input validation
        if not chat_request.message or len(chat_request.message.strip()) == 0:
            raise HTTPException(
                HTTP_STATUS_BAD_REQUEST, "Message cannot be empty"
            )

        if len(chat_request.message) > MAX_MESSAGE_LENGTH:
            raise HTTPException(
                HTTP_STATUS_BAD_REQUEST,
                "Message too long, max %d characters" % MAX_MESSAGE_LENGTH,
            )

        # Input sanitization
        sanitizer = InputSanitizer()
        sanitized_message = sanitizer.sanitize(chat_request.message)

        if not sanitized_message:
            raise HTTPException(
                HTTP_STATUS_BAD_REQUEST,
                "Message contains invalid content",
            )

        logger.info(
            "Chat request from %s (session=%s): %s...",
            user_ip,
            session_id,
            sanitized_message[:50],
        )

        # Check cache for intent classification
        message_hash = hashlib.md5(sanitized_message.encode()).hexdigest()
        cached_result = cache_service.get_intent_result(message_hash)

        # Process message
        try:
            result = await service.process_message(
                sanitized_message,
                session_id,
                chat_request.language,
            )
        except Exception as e:
            logger.error("Message processing failed: %s", e)
            audit_service.log_error(
                session_id,
                user_ip,
                str(e),
                "MESSAGE_PROCESSING_ERROR",
                "/api/chat",
                {"original_message_length": len(chat_request.message)},
            )
            raise HTTPException(
                HTTP_STATUS_INTERNAL_SERVER_ERROR,
                "Unable to process message",
            ) from e

        # Log to audit trail
        audit_service.log_chat(
            session_id,
            user_ip,
            sanitized_message[:200],
            result.get("intent", "unknown"),
            result.get("response", "")[:200],
            "success",
            {"message_length": len(sanitized_message)},
        )

        # Cache intent result
        if cached_result:
            cache_service.set_intent_result(
                message_hash,
                result.get("intent", "general"),
                0.9,
            )

        logger.info(
            "Chat response sent to %s (session=%s), intent=%s",
            user_ip,
            session_id,
            result.get("intent"),
        )

        return ChatResponse(
            response=result.get("response", ""),
            intent=result.get("intent", "general"),
            follow_up_suggestions=result.get("follow_up_suggestions", []),
            sources=result.get("sources", []),
            session_id=session_id,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unhandled chat error: %s", exc)
        audit_service.log_error(
            session_id,
            user_ip,
            str(exc),
            "UNHANDLED_ERROR",
            "/api/chat",
        )
        raise HTTPException(
            HTTP_STATUS_INTERNAL_SERVER_ERROR,
            "Internal server error",
        ) from exc
