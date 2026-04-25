"""Module: models.py
Description: Pydantic models for request and response validation.
Author: Praveen Kumar
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request model."""

    message: str = Field(..., min_length=1, description="User's message")
    session_id: Optional[str] = Field(
        None, description="Unique session identifier for conversation tracking"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    response: str = Field(..., description="Assistant's response message")
    intent: str = Field(..., description="Classified intent category")
    follow_up_suggestions: List[str] = Field(
        ..., description="Suggested follow-up questions"
    )
    sources: List[str] = Field(..., description="Information sources consulted")


class TimelineResponse(BaseModel):
    """Response model for timeline endpoint."""

    election_year: int = Field(..., description="Election year")
    events: List[dict] = Field(..., description="Complete election timeline events")
    upcoming: List[dict] = Field(..., description="Upcoming events within next 30 days")
    deadlines: dict = Field(..., description="Key deadline information")


class SystemStatusResponse(BaseModel):
    """Response model for system status endpoint."""

    project_id: str = Field(..., description="GCP project ID")
    project_number: str = Field(..., description="GCP project number")
    region: str = Field(..., description="GCP region")
    google_api_key_configured: bool = Field(
        ..., description="Whether Google API key is configured"
    )
    cloud_run_service_url_configured: bool = Field(
        ..., description="Whether Cloud Run URL is configured"
    )


class ElectionStep(BaseModel):
    """Structured step-by-step guidance model."""

    step_id: str = Field(..., description="Unique step identifier")
    title: str = Field(..., description="Step title")
    description: str = Field(..., description="Step description")
    actions: List[str] = Field(..., description="List of actions to take")
    estimated_time: str = Field(..., description="Estimated time to complete")
    resources: List[str] = Field(..., description="Helpful resources")
