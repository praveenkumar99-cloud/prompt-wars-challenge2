import os.path
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive.file'
]

def get_credentials():
    """Gets valid user credentials using Application Default Credentials (ADC)."""
    creds, project = google.auth.default(scopes=SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds
