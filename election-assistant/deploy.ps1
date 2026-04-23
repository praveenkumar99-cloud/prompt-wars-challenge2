# Deployment script for Google Cloud Run using Cloud Build
# Run this script from the project root directory

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,

    [Parameter(Mandatory=$true)]
    [string]$GoogleApiKey,

    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "election-assistant",

    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1"
)

Write-Host "Starting deployment to Google Cloud Run..." -ForegroundColor Cyan

# Set the project
Write-Host "Setting Google Cloud project to: $ProjectId" -ForegroundColor Yellow
gcloud config set project $ProjectId

# Enable required APIs
Write-Host "Enabling required Google Cloud APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Use Cloud Build to build and deploy directly to Cloud Run
Write-Host "Building and deploying using Google Cloud Build..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --source . `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --port 8080 `
    --set-env-vars "GOOGLE_API_KEY=$GoogleApiKey,GEMINI_MODEL=gemini-pro,ELECTION_COUNTRY=USA,ELECTION_YEAR=2024"

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Your service is now running on Google Cloud Run." -ForegroundColor Green