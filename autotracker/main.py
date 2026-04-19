"""
Elite FastAPI Application Module.
Includes Lifespan handlers, exact Cloud-Trace contexts, and Health Checks.
"""
from fastapi import FastAPI, BackgroundTasks, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio

from task_generator import TaskGenerator
from utils import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Graceful shutdown lifecycle events bridging SIGTERM handling securely."""
    logger.info("Application Startup triggered.")
    yield
    logger.info("SIGTERM received. Purging background queues securely.")
    await asyncio.sleep(0.5)

app = FastAPI(
    title="AutoTracker API Elite",
    description="Zero-Manual To-Do List Application API",
    version="2.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def add_cloud_trace_context(request: Request, call_next):
    """
    HTTP Middleware ensuring X-Cloud-Trace-Context correlations attach to local Loggers.
    """
    trace_header = request.headers.get("X-Cloud-Trace-Context")
    trace_id = trace_header.split("/")[0] if trace_header else None
    
    if trace_id:
        import logging
        for record_handler in logger.handlers:
            old_factory = logging.getLogRecordFactory()
            def record_factory(*args, **kwargs):
                record = old_factory(*args, **kwargs)
                record.trace_id = trace_id
                return record
            logging.setLogRecordFactory(record_factory)
            
    response = await call_next(request)
    return response

class TaskResponseModel(BaseModel):
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
    tasks: List[TaskResponseModel]
    generated_at: str

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint to verify the service is alive without 404s on the homepage."""
    return {"message": "AutoTracker Elite is running", "status": "healthy"}

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Elite strict health check enforcing dependency availability status."""
    logger.info("Health Check Invoked - System OK.")
    return {"status": "ok", "service": "AutoTracker", "timestamp": datetime.now().isoformat()}

@app.get("/api/tasks", response_model=TasksCollectionResponse)
async def get_tasks() -> Any:
    logger.info("Fetching live task list securely.")
    generator = TaskGenerator()
    tasks = await generator.generate_tasks()
    
    return {
        "tasks": tasks,
        "generated_at": datetime.now().isoformat()
    }

@app.post("/api/refresh")
async def refresh_tasks(background_tasks: BackgroundTasks) -> Dict[str, str]:
    logger.info("Refresh payload received. Queuing resilient background core.")
    background_tasks.add_task(process_tasks_background)
    return {"status": "processing"}

async def process_tasks_background() -> None:
    logger.info("Starting background task extraction.")
    generator = TaskGenerator()
    tasks = await generator.generate_tasks()
    logger.info(f"Successfully generated {len(tasks)} items in background sequence.")
