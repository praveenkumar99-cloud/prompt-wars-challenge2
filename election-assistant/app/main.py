import uvicorn
from .server import create_app

def example_run_server():
    """Example method showcasing how we start the FastAPI server programmatically"""
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    example_run_server()
