$env:PATH += ";C:\Users\konat_h9e4sxl\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
gcloud config set project praveen-space
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

gcloud services enable gmail.googleapis.com calendar-json.googleapis.com drive.googleapis.com run.googleapis.com cloudtasks.googleapis.com
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

gcloud builds submit --tag gcr.io/praveen-space/autotracker
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

gcloud run deploy autotracker-backend --image gcr.io/praveen-space/autotracker --platform managed --region us-central1 --allow-unauthenticated --memory 512Mi
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output "Deployment finished successfully. Please grab the URL from the output above to run the scheduler."
