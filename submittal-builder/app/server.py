from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
from .routes import upload_router, status_router, download_router

app = FastAPI(title="Submittal Builder")

app.include_router(upload_router)
app.include_router(status_router)
app.include_router(download_router)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open(os.path.join(os.path.dirname(__file__), "templates", "index.html"), "r") as f:
        return f.read()
