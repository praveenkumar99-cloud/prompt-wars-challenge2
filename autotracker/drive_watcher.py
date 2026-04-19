"""
Drive Watcher Module.

This module monitors Google Drive for recently modified or shared files
requiring attention.
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta
from google.auth import default
from googleapiclient.discovery import build

from utils import logger, cache_results

class DriveWatcher:
    """
    Monitors Google Drive for files requiring attention.
    """
    
    def __init__(self) -> None:
        """Initializes the Drive API client."""
        logger.info("Initializing DriveWatcher")
        credentials, project = default()
        self.service = build('drive', 'v3', credentials=credentials)
    
    @cache_results(maxsize=50)
    def _build_query(self, days_back: int) -> str:
        """
        Builds the search query for Drive API.
        
        Args:
            days_back (int): The number of days to look back for formatting.
            
        Returns:
            str: The raw Drive search query string.
        """
        return f"modifiedTime > '{datetime.now() - timedelta(days=days_back)}'"

    async def fetch_recent_changes(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch recently modified or shared files asynchronously.
        
        Args:
            days_back (int): Number of days to look back for recent changes.
            
        Returns:
            List[Dict[str, Any]]: A list of task dictionaries relating to Drive updates.
        """
        logger.info(f"Fetching recent drive changes for the last {days_back} days")
        query = self._build_query(days_back)
        
        try:
            results = await asyncio.to_thread(
                self.service.files().list(
                    q=query, 
                    fields="files(id, name, owners, lastModifyingUser)"
                ).execute
            )
            
            tasks = []
            for file in results.get('files', []):
                email_address = file.get('lastModifyingUser', {}).get('emailAddress')
                if email_address and email_address != 'me':
                    tasks.append({
                        'title': f"Review changes in: {file.get('name', 'Untitled Document')}",
                        'urgency_score': 50,
                        'importance_score': 50,
                        'effort_score': 20,
                        'category': "Work",
                        'source': 'drive',
                        'file_id': file['id']
                    })
                    
            logger.info(f"Extracted {len(tasks)} tasks from Drive.")
            return tasks
        except Exception as e:
            logger.error(f"Error fetching drive changes: {e}")
            return []
