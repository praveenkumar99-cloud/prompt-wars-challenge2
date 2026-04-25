"""Module: server.py
Description: FastAPI application factory and configuration.
Author: Praveen Kumar
"""
import logging
import os
from time import perf_counter
from typing import Any, Callable, Dict

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import config
from .models import SystemStatusResponse
from .routes.chat import router as chat_router
from .routes.steps import router as steps_router
from .routes.timeline import router as timeline_router

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("election-assistant")


def get_system_status() -> Dict[str, Any]:
    """Summarize the current runtime configuration.

    Returns:
        Dictionary containing configuration status.
    """
    return {
        "project_id": config.GCP_PROJECT_ID,
        "project_number": config.GCP_PROJECT_NUMBER,
        "region": config.GCP_REGION,
        "google_api_key_configured": bool(config.GOOGLE_API_KEY),
        "cloud_run_service_url_configured": bool(config.CLOUD_RUN_SERVICE_URL),
    }


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Initializes Google Cloud Logging if available, validates configuration,
    sets up middleware, mounts static files, and includes all route routers.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    # Validate configuration
    config.validate()

    # Initialize Google Cloud Logging
    try:
        from google.cloud import logging as gcp_logging

        gcp_client = gcp_logging.Client(project=config.GCP_PROJECT_ID)
        gcp_client.setup_logging()
        logger.info("Google Cloud Logging initialized")
    except Exception as e:
        # Broad catch: Cloud Logging is optional; continue without it
        logger.warning("Google Cloud Logging initialization failed: %s", e)

    app = FastAPI(title="Election Assistant", version="1.0.0")

    # NOTE: allow_origins=["*"] is intentional for hackathon demo.
    # Restrict to specific origins before production deployment.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(chat_router)
    app.include_router(timeline_router)
    app.include_router(steps_router)

    # Mount static files
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")

    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Routes
    @app.get("/", response_class=HTMLResponse)
    async def get_frontend() -> str:
        """Serve the main chat interface HTML page.

        Returns:
            HTML string of the chat interface.
        """
        index_path = os.path.join(templates_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as file:
                return file.read()
        return "<h1>Election Assistant</h1>"

    from .models import SystemStatusResponse

    @app.get(
        "/api/system/status",
        response_model=SystemStatusResponse,
        tags=["system"],
        summary="Get system configuration status",
    )
    async def system_status() -> SystemStatusResponse:
        """Expose a compact deployment status summary.

        Returns:
            SystemStatusResponse with project and configuration info.
        """
        return get_system_status()  # type: ignore[return-value]

    # Middleware
    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable) -> object:
        """Log HTTP request details and timing.

        Args:
            request: Incoming HTTP request.
            call_next: Next middleware in chain.

        Returns:
            Response object from downstream handler.
        """
        start_time = perf_counter()
        response = await call_next(request)
        process_time = perf_counter() - start_time
        response.headers["x-process-time"] = f"{process_time:.6f}"
        logger.info(
            {
                "method": request.method,
                "url": request.url.path,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
            }
        )
        return response

    return app
