"""Module: server.py
Description: FastAPI application factory with security headers and rate limiting.
Author: Praveen Kumar
"""
import logging
import os
from typing import Any, Callable, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import config
from .constants import (
    LOG_GCP_LOGGING_FAILED,
    LOG_GCP_LOGGING_INIT,
    SERVICE_STATUS_ERROR,
    SERVICE_STATUS_READY,
    SECURITY_HEADER_HSTS,
    SECURITY_HEADER_PERMISSIONS_POLICY,
    SECURITY_HEADER_REFERRER_POLICY,
    SECURITY_HEADER_X_CONTENT_TYPE_OPTIONS,
    SECURITY_HEADER_X_FRAME_OPTIONS,
    SECURITY_HEADER_X_XSS_PROTECTION,
)
from .models import SystemStatusResponse
from .routes.chat import router as chat_router
from .routes.steps import router as steps_router
from .routes.timeline import router as timeline_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("election-assistant")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def get_system_status() -> SystemStatusResponse:
    """Summarize the current runtime configuration.

    Returns:
        SystemStatusResponse with all service statuses.
    """
    return SystemStatusResponse(
        project_id=config.GCP_PROJECT_ID,
        project_number=config.GCP_PROJECT_NUMBER,
        region=config.GCP_REGION,
        google_api_key_configured=bool(config.GOOGLE_API_KEY),
        cloud_run_service_url_configured=bool(config.CLOUD_RUN_SERVICE_URL),
        vertex_ai_enabled=config.ENABLE_VERTEX_AI,
        firestore_enabled=config.ENABLE_FIRESTORE,
        cloud_storage_enabled=config.ENABLE_CLOUD_STORAGE and bool(
            config.GCS_BUCKET_NAME
        ),
        redis_cache_enabled=config.ENABLE_REDIS_CACHE,
    )


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Initializes all GCP services, security middleware, rate limiting,
    and includes all route routers.

    Returns:
        FastAPI: Fully configured FastAPI application instance.
    """
    # Validate configuration
    config.validate()

    # Initialize Google Cloud Logging
    try:
        from google.cloud import logging as gcp_logging

        gcp_client = gcp_logging.Client(project=config.GCP_PROJECT_ID)
        gcp_client.setup_logging()
        logger.info(LOG_GCP_LOGGING_INIT)
    except Exception as e:
        logger.warning(LOG_GCP_LOGGING_FAILED, e)

    app = FastAPI(
        title="Election Assistant",
        version="2.0.0",
        description="Comprehensive election guidance using Google Cloud services",
    )

    # Add rate limiter
    app.state.limiter = limiter

    # Add GZIP compression middleware
    app.add_middleware(GZIPMiddleware, minimum_size=1000)

    # Configure CORS with strict settings
    cors_origins = config.API_CORS_ORIGINS
    if cors_origins != ["*"]:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["Content-Type", "Authorization"],
            max_age=86400,
        )
    else:
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

    # Health check endpoint
    @app.get("/health", response_model=SystemStatusResponse)
    @limiter.limit("100/minute")
    async def health_check(request: Request) -> SystemStatusResponse:
        """Health check endpoint with system status.

        Args:
            request: HTTP request.

        Returns:
            SystemStatusResponse with current service statuses.
        """
        logger.info("Health check from %s", request.client.host)
        return get_system_status()

    # Frontend endpoint
    @app.get("/", response_class=HTMLResponse)
    @limiter.limit("100/minute")
    async def get_frontend(request: Request) -> str:
        """Serve the main chat interface HTML page.

        Args:
            request: HTTP request.

        Returns:
            HTML string of the chat interface.
        """
        index_path = os.path.join(templates_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as file:
                return file.read()
        return "<h1>Election Assistant</h1>"

    # Status endpoint
    @app.get("/api/status", response_model=SystemStatusResponse)
    @limiter.limit("100/minute")
    async def status(request: Request) -> SystemStatusResponse:
        """Get detailed system status.

        Args:
            request: HTTP request.

        Returns:
            SystemStatusResponse with service configuration.
        """
        logger.info("Status request from %s", request.client.host)
        return get_system_status()

    return app

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

    from .models import SystemStatusResponse

    @app.get(
        "/health",
        tags=["system"],
        summary="Health check endpoint",
    )
    async def health_check() -> dict:
        """Health check endpoint for load balancers and monitoring.

        Returns:
            Dictionary with service health status.
        """
        status = get_system_status()
        return {
            "status": "healthy",
            "project_id": status.get("project_id", ""),
            "region": status.get("region", ""),
            "google_api_key_configured": status.get("google_api_key_configured", False),
            "vertex_ai_enabled": getattr(config, "ENABLE_VERTEX_AI", False),
            "firestore_enabled": getattr(config, "ENABLE_FIRESTORE", False),
            "redis_enabled": getattr(config, "ENABLE_REDIS_CACHE", False),
        }

    @app.get(
        "/api/status",
        response_model=SystemStatusResponse,
        tags=["system"],
        summary="API status endpoint alias",
    )
    async def api_status() -> SystemStatusResponse:
        """Alias for system status — used by monitoring tools.

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
