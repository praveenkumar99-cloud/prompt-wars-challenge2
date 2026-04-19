"""
Drive Watcher Module - Buildathon Edition.
Uses native httpx for REST logic mapping properly to global application Client session.
"""
from typing import List, Dict, Any, TypedDict, Optional
from datetime import datetime, timedelta
import httpx
import google.auth
import google.auth.transport.requests

from utils import logger, cache_results, resilient_api_call

class UserDict(TypedDict, total=False):
    emailAddress: str

class FileItem(TypedDict, total=False):
    id: str
    name: str
    lastModifyingUser: UserDict

class DriveResponse(TypedDict):
    files: List[FileItem]

class DriveWatcher:
    """Monitors Google Drive REST API."""
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.headers = {}
    
    async def initialize(self) -> None:
        logger.info("Initializing DriveWatcher bindings async.")
        credentials, _ = google.auth.default()
        req = google.auth.transport.requests.Request()
        credentials.refresh(req)
        self.headers = {"Authorization": f"Bearer {credentials.token}"}
    
    @cache_results(maxsize=50)
    def _build_query(self, days_back: int) -> str:
        return f"modifiedTime > '{datetime.now() - timedelta(days=days_back)}'"

    @resilient_api_call()
    async def fetch_recent_changes(self, days_back: int = 7) -> List[Dict[str, Any]]:
        query = self._build_query(days_back)
        url = "https://www.googleapis.com/drive/v3/files"
        params = {"q": query, "fields": "files(id,name,owners,lastModifyingUser)"}
        
        response = await self.client.get(url, headers=self.headers, params=params, timeout=10.0)
        response.raise_for_status()
        data: DriveResponse = response.json()
        
        tasks = []
        for file in data.get('files', []):
            email_address = file.get('lastModifyingUser', {}).get('emailAddress')
            if email_address and email_address != 'me':
                tasks.append({
                    'title': f"Review changes in: {file.get('name', 'Untitled Document')}",
                    'urgency_score': 50,
                    'importance_score': 50,
                    'effort_score': 20,
                    'category': "Work",
                    'source': 'drive',
                    'file_id': file.get('id')
                })
        return tasks
