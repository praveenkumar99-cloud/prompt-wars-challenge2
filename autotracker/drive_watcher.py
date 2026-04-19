from google.auth import default
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict

class DriveWatcher:
    """Monitors Google Drive for files requiring attention"""
    
    def __init__(self):
        credentials, project = default()
        self.service = build('drive', 'v3', credentials=credentials)
    
    def fetch_recent_changes(self, days_back: int = 7) -> List[Dict]:
        """Fetch recently modified or shared files"""
        query = f"modifiedTime > '{datetime.now() - timedelta(days=days_back)}'"
        results = self.service.files().list(q=query, fields="files(id, name, owners, lastModifyingUser)").execute()
        
        tasks = []
        for file in results.get('files', []):
            if file.get('lastModifyingUser', {}).get('emailAddress') != 'me':
                tasks.append({
                    'title': f"Review changes in: {file['name']}",
                    'source': 'drive',
                    'file_id': file['id']
                })
        return tasks
