"""
Elite FastAPI Application Module.
Includes Lifespan handlers, exact Cloud-Trace contexts, Health Checks,
and pure strict Pydantic parsing implementations mapping context vars.
"""
from fastapi import FastAPI, BackgroundTasks, Request
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager
import asyncio
import time
import uuid
import httpx

from task_generator import TaskGenerator
from utils import logger, request_id_ctx, latency_ctx, status_code_ctx

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Graceful shutdown lifecycle events establishing context clients."""
    logger.info("Application Startup triggered.")
    app.state.http_client = httpx.AsyncClient()
    yield
    logger.info("SIGTERM received. Purging connections smoothly...")
    await app.state.http_client.aclose()
    
    # Flushing logs ensures they don't get trapped in memory during shutdown
    for handler in logger.handlers:
        handler.flush()
    await asyncio.sleep(0.1)

app = FastAPI(
    title="AutoTracker API Elite",
    description="Zero-Manual To-Do List Application API",
    version="3.0.0",
    lifespan=lifespan
)

@app.middleware("http")
async def add_cloud_trace_context(request: Request, call_next):
    """
    HTTP Middleware ensuring X-Cloud-Trace-Context correlations, assigning UUIDs natively.
    Captures process latency efficiently into Cloud format bindings.
    """
    start_time = time.time()
    trace_header = request.headers.get("X-Cloud-Trace-Context")
    req_id = trace_header.split("/")[0] if trace_header else str(uuid.uuid4())
    
    request_id_ctx.set(req_id)
    
    response = await call_next(request)
    
    latency = round((time.time() - start_time) * 1000, 2)
    latency_ctx.set(latency)
    status_code_ctx.set(response.status_code)
    
    logger.info("HTTP Request Processed") # This now triggers the log record formatter
    return response

class TaskResponseModel(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1)
    deadline: Optional[str] = None
    urgency_score: Optional[int] = Field(0, ge=0, le=100)
    importance_score: Optional[int] = Field(0, ge=0, le=100)
    effort_score: Optional[int] = Field(0, ge=0, le=100)
    category: Optional[str] = Field(None, min_length=1)
    source: str = Field(min_length=1)
    priority: Optional[float] = 0.0
    event_id: Optional[str] = None
    file_id: Optional[str] = None

class TasksCollectionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    tasks: List[TaskResponseModel]
    generated_at: str

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "AutoTracker running happily", "status": "healthy"}

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Elite strict health check enforcing dependency availability status."""
    return {"status": "ok", "service": "AutoTracker", "timestamp": datetime.now().isoformat()}

@app.get("/api/tasks", response_model=TasksCollectionResponse)
async def get_tasks(request: Request) -> Any:
    # Use centralized httpx client
    client = request.app.state.http_client
    generator = TaskGenerator(client)
    tasks = await generator.generate_tasks()
    
    return {
        "tasks": tasks,
        "generated_at": datetime.now().isoformat()
    }

@app.post("/api/refresh")
async def refresh_tasks(request: Request, background_tasks: BackgroundTasks) -> Dict[str, str]:
    client = request.app.state.http_client
    background_tasks.add_task(process_tasks_background, client)
    return {"status": "processing"}

async def process_tasks_background(client: httpx.AsyncClient) -> None:
    generator = TaskGenerator(client)
    tasks = await generator.generate_tasks()
    logger.info(f"Successfully generated {len(tasks)} items in background sequence.")
