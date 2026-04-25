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
    [string]$Region = "us-central1",

    [Parameter(Mandatory=$false)]
    [string]$ProjectNumber = "665822784067"
)

$GeminiSecretName = "election-assistant-gemini-api-key"
$RuntimeServiceAccount = "$ProjectNumber-compute@developer.gserviceaccount.com"
$ServiceUrl = "https://$ServiceName-$ProjectNumber.$Region.run.app"

Write-Host "Starting deployment to Google Cloud Run..." -ForegroundColor Cyan

Write-Host "Setting Google Cloud project to: $ProjectId" -ForegroundColor Yellow
gcloud config set project $ProjectId

Write-Host "Enabling required Google Cloud APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

Write-Host "Ensuring Secret Manager secret exists: $GeminiSecretName" -ForegroundColor Yellow
gcloud secrets describe $GeminiSecretName --project $ProjectId *> $null
if ($LASTEXITCODE -ne 0) {
    gcloud secrets create $GeminiSecretName --replication-policy=automatic --project $ProjectId
}
$GoogleApiKey | gcloud secrets versions add $GeminiSecretName --data-file=- --project $ProjectId

Write-Host "Granting Secret Manager access to Cloud Run runtime service account" -ForegroundColor Yellow
gcloud secrets add-iam-policy-binding $GeminiSecretName --member="serviceAccount:$RuntimeServiceAccount" --role="roles/secretmanager.secretAccessor" --project $ProjectId *> $null

Write-Host "Building and deploying using Google Cloud Build..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --source . `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --port 8080 `
    --set-env-vars "GEMINI_MODEL=gemini-3-flash,ELECTION_COUNTRY=USA,ELECTION_YEAR=2024,GCP_PROJECT_ID=$ProjectId,GCP_PROJECT_NUMBER=$ProjectNumber,GCP_REGION=$Region,CLOUD_RUN_SERVICE_URL=$ServiceUrl" `
    --set-secrets "GOOGLE_API_KEY=${GeminiSecretName}:latest"

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host "Your service is now running on Google Cloud Run." -ForegroundColor Green
Write-Host "Service URL: $ServiceUrl" -ForegroundColor Green
