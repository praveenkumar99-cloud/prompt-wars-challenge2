# AI-Powered Election Process Assistant

## Vertical
**Civic Tech & Public Information** - Helping citizens understand election processes, timelines, and steps through interactive AI assistance.

## Approach
Multi-intent understanding using Google's Gemini 1.5 Pro for:
- Natural language understanding of election-related queries
- Context-aware responses about registration, voting, deadlines
- Step-by-step guidance for election participation

## How It Works
`User asks question -> Gemini classifies intent -> Retrieve relevant info -> Generate personalized response -> Interactive follow-up`

## Setup Instructions

### Prerequisites
- Python 3.11+
- Google Gemini API key ([Get here](https://aistudio.google.com/apikey))

### Installation
```bash
# Clone repository
git clone <your-repo-url>
cd election-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run the application
uvicorn app.main:app --reload --port 8000
```

### Testing
```bash
python -m pytest tests/ -v
```

## Deployment to Google Cloud Run

### Prerequisites
- Google Cloud SDK installed and authenticated (`gcloud auth login`)
- Docker installed
- A Google Cloud Project with billing enabled

### Deployment Steps
1. Set your Google Cloud Project ID:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. Enable required APIs:
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
   ```

3. Run the deployment script:
   ```powershell
   .\deploy.ps1 -ProjectId YOUR_PROJECT_ID -GoogleApiKey YOUR_GEMINI_API_KEY
   ```

   The deployment uses **gemini-1.5-pro** and stores the Gemini API key in **Secret Manager**.

4. The script will:
   - Build the Docker image
   - Store the Gemini API key in Secret Manager
   - Deploy to Cloud Run
   - Display the service URL

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web chat interface |
| POST | `/api/chat` | Send message to assistant |
| GET | `/api/timeline` | Get election timeline |
| GET | `/api/steps/{step_id}` | Get detailed step information |
| GET | `/api/system/status` | Verify configured Google service integrations |

## Demo Questions to Ask
- "How do I register to vote?"
- "What are the important election deadlines?"
- "When is the primary election?"
- "How can I vote by mail?"
- "What documents do I need to bring to vote?"
- "Where is my polling place?"
