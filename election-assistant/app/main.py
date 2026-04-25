"""Module: main.py
Description: Application entry point for local development.
Author: Praveen Kumar
"""
import uvicorn
from .server import create_app

app = create_app()


def run_server() -> None:
    """Run the FastAPI application locally.

    Starts the development server on 0.0.0.0:8000 with auto-reload enabled.
    """
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run_server()
