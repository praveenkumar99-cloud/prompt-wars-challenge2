"""Module: models.py
Description: Pydantic models for request and response validation with comprehensive type hints.
Author: Praveen Kumar
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request model.

    Attributes:
        message: User's election-related question or query.
        session_id: Optional unique session identifier for conversation tracking.
        language: Optional language code (default: 'en').
    """

    message: str = Field(
        ...,
        description="User's election-related question",
    )
    session_id: Optional[str] = Field(
        None, description="Unique session identifier for conversation tracking"
    )
    language: str = Field(
        "en", description="Language code (en/es) for response"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint.

    Attributes:
        response: Assistant's generated response message.
        intent: Classified intent category from the user message.
        follow_up_suggestions: Recommended follow-up questions.
        sources: Information sources consulted for the response.
        session_id: Session identifier for tracking conversation.
    """

    response: str = Field(..., description="Assistant's response message")
    intent: str = Field(..., description="Classified intent category")
    follow_up_suggestions: List[str] = Field(
        ..., description="Suggested follow-up questions (max 3)"
    )
    sources: List[str] = Field(..., description="Information sources consulted")
    session_id: Optional[str] = Field(
        None, description="Session identifier for tracking"
    )


class TimelineEvent(BaseModel):
    """Individual timeline event.

    Attributes:
        event_id: Unique event identifier.
        title: Event title or name.
        date: Event date (ISO format).
        description: Detailed event description.
        is_deadline: Whether this is a critical deadline.
    """

    event_id: str = Field(..., description="Unique event identifier")
    title: str = Field(..., description="Event title")
    date: str = Field(..., description="Event date (ISO 8601 format)")
    description: str = Field(..., description="Detailed event description")
    is_deadline: bool = Field(
        False, description="Whether this is a critical deadline"
    )


class TimelineResponse(BaseModel):
    """Response model for timeline endpoint.

    Attributes:
        election_year: The election year.
        events: Complete list of timeline events.
        upcoming: Events within next 30 days.
        deadlines: Key deadline information.
    """

    election_year: int = Field(..., description="Election year")
    events: List[TimelineEvent] = Field(..., description="Complete timeline events")
    upcoming: List[TimelineEvent] = Field(
        ..., description="Upcoming events within 30 days"
    )
    deadlines: Dict[str, str] = Field(..., description="Key deadline information")


class SystemStatusResponse(BaseModel):
    """Response model for system status endpoint.

    Attributes:
        project_id: GCP project ID.
        project_number: GCP project number.
        region: GCP region.
        google_api_key_configured: API key status.
        cloud_run_service_url_configured: Cloud Run URL status.
        vertex_ai_enabled: Vertex AI service status.
        firestore_enabled: Firestore persistence status.
        cloud_storage_enabled: Cloud Storage status.
        redis_cache_enabled: Redis cache status.
    """

    project_id: str = Field(..., description="GCP project ID")
    project_number: str = Field(..., description="GCP project number")
    region: str = Field(..., description="GCP region")
    google_api_key_configured: bool = Field(
        ..., description="Whether Google API key is configured"
    )
    cloud_run_service_url_configured: bool = Field(
        ..., description="Whether Cloud Run URL is configured"
    )
    vertex_ai_enabled: bool = Field(..., description="Vertex AI service status")
    firestore_enabled: bool = Field(..., description="Firestore persistence status")
    cloud_storage_enabled: bool = Field(..., description="Cloud Storage status")
    redis_cache_enabled: bool = Field(..., description="Redis cache status")


class ElectionStep(BaseModel):
    """Structured step-by-step guidance model.

    Attributes:
        step_id: Unique step identifier.
        title: Step title.
        description: Detailed step description.
        actions: Ordered list of actions to complete.
        estimated_time: Estimated time to complete.
        resources: Helpful resources and links.
    """

    step_id: str = Field(..., description="Unique step identifier")
    title: str = Field(..., description="Step title")
    description: str = Field(..., description="Step description")
    actions: List[str] = Field(..., description="List of actions to take")
    estimated_time: str = Field(..., description="Estimated time to complete")
    resources: List[str] = Field(..., description="Helpful resources")


class AuditLog(BaseModel):
    """Audit log entry for compliance tracking.

    Attributes:
        action: Type of action performed.
        user_id: User identifier (session or anon).
        ip_address: Client IP address.
        message: Request message content.
        intent: Classified intent.
        status: Success/failure status.
        timestamp: When the action occurred.
        metadata: Additional context.
    """

    action: str = Field(..., description="Type of action")
    user_id: str = Field(..., description="User identifier")
    ip_address: str = Field(..., description="Client IP address")
    message: Optional[str] = Field(None, description="Request message")
    intent: Optional[str] = Field(None, description="Classified intent")
    status: str = Field(..., description="Success/failure status")
    timestamp: datetime = Field(..., description="Action timestamp")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )


class PDFExportRequest(BaseModel):
    """Request model for PDF export.

    Attributes:
        session_id: Session to export.
        include_sources: Whether to include sources.
        language: Language code for export.
    """

    session_id: Optional[str] = Field(None, description="Session to export")
    include_sources: bool = Field(
        True, description="Include sources in export"
    )
    language: str = Field("en", description="Language code")


class PDFExportResponse(BaseModel):
    """Response model for PDF export.

    Attributes:
        url: Signed URL to download PDF.
        expires_in: Seconds until URL expires.
        size_bytes: PDF file size.
    """

    url: str = Field(..., description="Signed download URL")
    expires_in: int = Field(..., description="Seconds until URL expires")
    size_bytes: int = Field(..., description="PDF file size")
