# AI-Powered Election Process Assistant

## Project Overview

The Election Assistant is an AI-powered civic information tool that helps citizens understand election processes, timelines, and voting steps through interactive chat. Built with FastAPI and Google's Gemini LLM, it provides accurate, non-partisan answers about voter registration, deadlines, voting methods, ID requirements, and polling locations.

## Tech Stack

- **FastAPI** - Modern Python web framework for API development
- **Google Gemini 2.5 Pro** - LLM for natural language understanding and response generation
- **Google Cloud Platform** - Cloud Run for deployment, Firestore for session persistence
- **Google Cloud Logging** - Structured logging and monitoring
- **Pydantic** - Data validation and serialization
- **Jinja2** - Template rendering for web interface

## Local Setup Instructions

### Prerequisites

- Python 3.11+ installed
- Google Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd election-assistant

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run the application
uvicorn app.main:app --reload --port 8000
```

The application will be available at `http://localhost:8000`.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Your Gemini API key from Google AI Studio | *(required)* |
| `GEMINI_MODEL` | Model to use for responses | `gemini-2.5-pro` |
| `GCP_PROJECT_ID` | Your GCP project ID | `praveen-space` |
| `GCP_PROJECT_NUMBER` | Your GCP project number | `665822784067` |
| `GCP_REGION` | Region for Cloud Run deployment | `us-central1` |
| `CLOUD_RUN_SERVICE_URL` | Deployed service URL | *(empty)* |
| `FIRESTORE_COLLECTION` | Firestore collection name | `chat_sessions` |
| `ELECTION_COUNTRY` | Election country | `USA` |
| `ELECTION_YEAR` | Election year | `2024` |

### Running Tests

```bash
# Run the full test suite
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ -v --cov=app
```

All tests use pytest with asyncio support for async endpoint testing.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web chat interface |
| `POST` | `/api/chat` | Send message to assistant |
| `GET` | `/api/timeline` | Get election timeline |
| `GET` | `/api/steps` | Get all step-by-step guides |
| `GET` | `/api/steps/{step_id}` | Get specific step-by-step guide |
| `GET` | `/api/system/status` | System configuration status |

### Chat Request/Response

**Request:**
```json
{
  "message": "How do I register to vote?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "You can register online, by mail, or in person...",
  "intent": "registration",
  "follow_up_suggestions": [
    "How do I check my registration status?",
    "What's the registration deadline?"
  ],
  "sources": [
    "USA.gov Voting & Election Information",
    "Your State Election Office Website"
  ]
}
```

## Deployment

### Cloud Build & Cloud Run

The project includes `cloudbuild.yaml` for automated deployment via Google Cloud Build.

**Prerequisites:**

- Google Cloud SDK installed and authenticated (`gcloud auth login`)
- Docker installed
- GCP project with billing enabled

**Deployment Steps:**

1. Set your Google Cloud Project ID:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. Enable required APIs:
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
   ```

3. Deploy using Cloud Build:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

   Or use the provided deployment script:
   ```powershell
   .\deploy.ps1 -ProjectId YOUR_PROJECT_ID -GoogleApiKey YOUR_GEMINI_API_KEY
   ```

The deployment:
- Builds Docker image and pushes to Container Registry
- Stores Gemini API key in Secret Manager
- Deploys to Cloud Run with managed platform
- Service is publicly accessible (`--allow-unauthenticated`)

## Demo Questions

- "How do I register to vote?"
- "What are the important election deadlines?"
- "When is the primary election?"
- "How can I vote by mail?"
- "What documents do I need to bring to vote?"
- "Where is my polling place?"

## Project Structure

```
election-assistant/
├── app/
│   ├── config.py           # Configuration management
│   ├── constants.py        # Application constants
│   ├── models.py           # Pydantic request/response models
│   ├── server.py           # FastAPI application factory
│   ├── main.py             # Entry point for local development
│   ├── routes/
│   │   ├── chat.py         # Chat endpoint
│   │   ├── steps.py        # Step-by-step guidance
│   │   └── timeline.py     # Election timeline
│   ├── services/
│   │   ├── assistant.py    # Main orchestrator
│   │   ├── gemini.py       # Gemini LLM integration
│   │   ├── intent.py       # Intent classification
│   │   ├── timeline.py     # Election dates
│   │   └── step.py         # Voting guidance
│   ├── templates/
│   │   └── index.html      # Chat UI
│   └── static/
│       ├── style.css       # Styles
│       └── script.js       # Frontend logic
├── tests/                  # Test suite
├── data/
│   └── election_knowledge.json  # Static election data
├── requirements.txt        # Python dependencies
├── cloudbuild.yaml         # Cloud Build configuration
├── Dockerfile              # Container specification
├── README.md              # This file
└── .env.example           # Environment variables template
```

## Notes

- This is a **Google PromptWars hackathon submission**
- Designed for scalability on Cloud Run (handles 1000+ concurrent users)
- Uses Firestore for session persistence across instances
- Falls back to template responses if Gemini API is unavailable
- All API responses are cached by Cloud CDN for faster subsequent requests
