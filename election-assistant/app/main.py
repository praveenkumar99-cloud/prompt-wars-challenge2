import uvicorn
from .server import create_app

app = create_app()

def run_server():
    """Run the FastAPI application locally."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_server()
