"""Pydantic models for request/response validation"""
from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PartNumberResult(BaseModel):
    part_number: str
    found_documents: List[str]
    is_valid: bool
    confidence: float

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_parts: Optional[int] = None
    missing_parts: Optional[List[str]] = None
    download_url: Optional[str] = None
    error_message: Optional[str] = None

class ExtractRequest(BaseModel):
    text: str

class ExtractResponse(BaseModel):
    part_numbers: List[str]
    raw_response: str
