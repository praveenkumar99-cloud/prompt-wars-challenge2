"""Pydantic models for request and response validation."""
from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Incoming chat request."""

    message: str
    session_id: Optional[str] = None


class ElectionStep(BaseModel):
    """Structured step-by-step guidance."""

    step_id: str
    title: str
    description: str
    actions: List[str]
    estimated_time: str
    resources: List[str]
