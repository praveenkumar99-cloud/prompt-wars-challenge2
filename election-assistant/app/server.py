"""FastAPI Application Factory"""
from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import logging
from .routes.chat import router as chat_router
from .routes.timeline import router as timeline_router
from .routes.steps import router as steps_router
from .config import firestore_client, auth
from google.cloud import storage
from google.cloud import tasks_v2
from google.cloud import aiplatform
from google.cloud import monitoring_v3

# Initialize Cloud Storage client
storage_client = storage.Client()
bucket_name = "your-bucket-name"
bucket = storage_client.bucket(bucket_name)

# Initialize Cloud Tasks client
tasks_client = tasks_v2.CloudTasksClient()
project = "your-gcp-project-id"
queue = "gemini-api-queue"
location = "us-central1"

# Initialize Vertex AI
aiplatform.init(project=project, location=location)

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("election-assistant")

# Initialize Cloud Monitoring client
monitoring_client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{project}"

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

    # Replace in-memory storage with Firestore collections
    sessions_collection = firestore_client.collection("sessions")
    messages_collection = firestore_client.collection("messages")
    user_preferences_collection = firestore_client.collection("user_preferences")

    @app.get("/", response_class=HTMLResponse)
    async def get_frontend():
        index_path = os.path.join(templates_dir, "index.html")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>Welcome to Election Assistant!</h1><p>UI is under construction.</p>"
        
    # Real-time listener for chat updates
    @app.websocket("/ws/chat/{session_id}")
    async def chat_websocket(websocket: WebSocket, session_id: str):
        await websocket.accept()

        # Firestore listener
        def on_snapshot(doc_snapshot, changes, read_time):
            for doc in doc_snapshot:
                websocket.send_json(doc.to_dict())

        query = messages_collection.where("session_id", "==", session_id)
        query_watch = query.on_snapshot(on_snapshot)

        try:
            while True:
                await websocket.receive_text()
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            query_watch.unsubscribe()

    @app.post("/auth/google-signin")
    async def google_signin(request: Request):
        body = await request.json()
        id_token = body.get("id_token")

        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token["uid"]
            user = auth.get_user(uid)
            return {"message": "Sign-in successful", "user": user.uid}
        except Exception as e:
            return {"error": str(e)}

    @app.get("/auth/session")
    async def get_session():
        # Example session persistence logic
        return {"message": "Session active"}

    @app.post("/store/conversation")
    async def store_conversation(request: Request):
        body = await request.json()
        session_id = body.get("session_id")
        conversation_data = body.get("conversation")

        blob = bucket.blob(f"conversations/{session_id}.json")
        blob.upload_from_string(conversation_data, content_type="application/json")
        return {"message": "Conversation stored successfully"}

    @app.get("/download/guide/{guide_id}")
    async def download_guide(guide_id: str):
        blob = bucket.blob(f"guides/{guide_id}.json")
        signed_url = blob.generate_signed_url(version="v4", expiration=3600, method="GET")
        return {"download_url": signed_url}

    @app.post("/tasks/gemini")
    async def create_gemini_task(request: Request):
        body = await request.json()
        payload = json.dumps(body)

        parent = tasks_client.queue_path(project, location, queue)
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": "https://your-cloud-run-service-url/gemini",
                "headers": {"Content-Type": "application/json"},
                "body": payload.encode(),
            }
        }

        try:
            response = tasks_client.create_task(request={"parent": parent, "task": task})
            return {"message": "Task created successfully", "task_name": response.name}
        except Exception as e:
            return {"error": str(e)}

    @app.post("/vertex-ai/gemini")
    async def vertex_ai_gemini(request: Request):
        body = await request.json()
        query = body.get("query")

        try:
            # Example: Vertex AI text-to-text model
            model = aiplatform.TextGenerationModel.from_pretrained("text-bison@001")
            response = model.predict(query)
            return {"response": response.text}
        except Exception as e:
            return {"error": str(e)}

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        response = await call_next(request)
        logger.info({"method": request.method, "url": request.url.path, "status_code": response.status_code})

        # Example: Custom metric for response time
        series = monitoring_v3.TimeSeries()
        series.metric.type = "custom.googleapis.com/response_time"
        series.resource.type = "global"
        point = series.points.add()
        point.value.double_value = response.headers.get("x-process-time", 0)
        point.interval.end_time.seconds = int(time.time())
        monitoring_client.create_time_series(name=project_name, time_series=[series])

        return response

    return app

# The instance that uvicorn runs or looks for
app = create_app()
