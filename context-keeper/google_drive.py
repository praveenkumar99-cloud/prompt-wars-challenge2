from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from auth import get_credentials
import io

def save_to_drive(filename, content):
    """Uploads text content as a Markdown file to Google Drive."""
    creds = get_credentials()
    if not creds:
        return None
        
    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': filename, 'mimeType': 'text/markdown'}
        
        # Convert content to file stream
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/markdown', resumable=True)
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        return file
    except Exception as e:
        print(f"Error saving to Google Drive: {e}")
        return None
