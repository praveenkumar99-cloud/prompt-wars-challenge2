# AI-Powered Submittal Builder

## Vertical
**Enterprise Automation** - Automating customer product submittal generation from Bills of Materials (BOMs)

## Approach
Multi-agent orchestration using Google's Gemini 1.5 Pro for:
- Intelligent part number extraction from unstructured BOMs
- Document relevance validation
- Automated submittal assembly

## How It Works
`User uploads BOM → Gemini extracts part numbers → Mock retrieval → Gemini validates → ZIP assembly → Download link`

## Setup Instructions

### Prerequisites
- Python 3.11+
- Google Gemini API key ([Get here](https://aistudio.google.com/apikey))

### Installation
```bash
# Clone repository
git clone <your-repo-url>
cd submittal-builder

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
pytest tests/ -v
```

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web interface |
| POST | `/api/upload` | Upload BOM file |
| GET | `/api/status/{job_id}` | Check job status |
| GET | `/api/download/{job_id}` | Download submittal ZIP |

## Assumptions
1. Document repository is mocked (real implementation would use Vertex AI Search with indexed documents)
2. Gemini API is accessible with valid API key
3. Local file storage for demo (production would use Cloud Storage)
4. Supported BOM formats: PDF, CSV, TXT (max 5MB)

## Demo
Use `sample_bom.txt` to test the application.
