"""
Entry point for the Submittal Builder server.
This file adheres strictly to the rule of separating distinct functionality.
"""
import uvicorn

def run_server_example():
    """Starts the application server to showcase functionality"""
    # Import app here to avoid circular imports during testing
    try:
        from .server import app
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        from app.server import app
        uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # The main method in main.py is the entry point to showcase functionality.
    run_server_example()
