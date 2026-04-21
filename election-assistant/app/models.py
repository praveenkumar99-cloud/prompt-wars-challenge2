"""Pydantic models for request/response validation"""
from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime

class IntentType(str, Enum):
    REGISTRATION = "registration"
    DEADLINES = "deadlines"
    VOTING_METHODS = "voting_methods"
    REQUIREMENTS = "requirements"
    POLLING_LOCATIONS = "polling_locations"
    CANDIDATES = "candidates"
    GENERAL = "general"

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: IntentType
    follow_up_suggestions: List[str]
    sources: List[str]

class TimelineEvent(BaseModel):
    event_name: str
    date: str
    description: str
    days_remaining: Optional[int] = None

class ElectionStep(BaseModel):
    step_id: str
    title: str
    description: str
    actions: List[str]
    estimated_time: str
    resources: List[str]
