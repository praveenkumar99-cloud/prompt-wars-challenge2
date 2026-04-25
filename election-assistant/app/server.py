"""FastAPI application factory."""
import logging
import os
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import config
from .routes.chat import router as chat_router
from .routes.steps import router as steps_router
from .routes.timeline import router as timeline_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("election-assistant")


def get_system_status() -> dict:
    """Summarize the current runtime configuration."""
    return {
        "project_id": config.GCP_PROJECT_ID,
        "project_number": config.GCP_PROJECT_NUMBER,
        "region": config.GCP_REGION,
        "google_api_key_configured": bool(config.GOOGLE_API_KEY),
        "cloud_run_service_url_configured": bool(config.CLOUD_RUN_SERVICE_URL),
    }


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Election Assistant", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router)
    app.include_router(timeline_router)
    app.include_router(steps_router)

    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")

    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def get_frontend():
        index_path = os.path.join(templates_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as file:
                return file.read()
        return "<h1>Election Assistant</h1>"

    @app.get("/api/system/status")
    async def system_status():
        """Expose a compact deployment status summary."""
        return get_system_status()

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
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


app = create_app()
