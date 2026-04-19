"""
Main FastAPI Application Module.

Serves endpoints for fetching tasks synchronously and asynchronously via Google Cloud Scheduler.
"""

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from task_generator import TaskGenerator
from utils import logger

app = FastAPI(
    title="AutoTracker API",
    description="Zero-Manual To-Do List Application API",
    version="1.0.0"
)

class TaskResponseModel(BaseModel):
    """Pydantic model describing a returned Task."""
    title: str
    deadline: Optional[str] = None
    urgency_score: Optional[int] = 0
    importance_score: Optional[int] = 0
    effort_score: Optional[int] = 0
    category: Optional[str] = None
    source: str
    priority: Optional[float] = 0.0
    event_id: Optional[str] = None
    file_id: Optional[str] = None

class TasksCollectionResponse(BaseModel):
    """Pydantic model representing the response envelope."""
    tasks: List[TaskResponseModel]
    generated_at: str

@app.get("/")
async def root() -> Dict[str, str]:
    """Health check endpoint."""
    logger.info("Health check ping received.")
    return {"message": "AutoTracker is running", "status": "healthy"}

@app.get("/api/tasks", response_model=TasksCollectionResponse)
async def get_tasks() -> Any:
    """
    Get the current task list extracted live from all Google Services.
    """
    logger.info("Fetching live task list.")
    generator = TaskGenerator()
    tasks = await generator.generate_tasks()
    
    return {
        "tasks": tasks,
        "generated_at": datetime.now().isoformat()
    }

@app.post("/api/refresh")
async def refresh_tasks(background_tasks: BackgroundTasks) -> Dict[str, str]:
    """
    Triggers task refresh, usually called by Cloud Scheduler.
    Executes heavily asynchronous extractions in the background.
    """
    logger.info("Refresh payload received. Queuing background job.")
    background_tasks.add_task(process_tasks_background)
    return {"status": "processing"}

async def process_tasks_background() -> None:
    """
    Background worker process. Executes generation routines asynchronously.
    """
    logger.info("Starting background task extraction.")
    generator = TaskGenerator()
    tasks = await generator.generate_tasks()
    logger.info(f"Successfully generated {len(tasks)} items in background sequence.")
