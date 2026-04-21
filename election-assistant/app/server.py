"""FastAPI Application Factory"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from .routes.chat import router as chat_router
from .routes.timeline import router as timeline_router
from .routes.steps import router as steps_router

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(title="Election Assistant", version="1.0.0")
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API Routers
    app.include_router(chat_router)
    app.include_router(timeline_router)
    app.include_router(steps_router)
    
    # Static and Templates
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def get_frontend():
        index_path = os.path.join(templates_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>Welcome to Election Assistant!</h1><p>UI is under construction.</p>"
        
    return app

# The instance that uvicorn runs or looks for
app = create_app()
