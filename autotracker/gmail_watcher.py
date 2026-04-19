from google.auth import default
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import re
from typing import List, Dict

class GmailWatcher:
    """Monitors Gmail for action items and tasks"""
    
    ACTION_KEYWORDS = ['action required', 'to do', 'task', 'please', 'follow up', 'reminder']
    
    def __init__(self):
        credentials, project = default()
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def fetch_action_emails(self, hours_back: int = 24) -> List[Dict]:
        """Fetch emails containing action keywords from last N hours"""
        query = f'newer_than:{hours_back}h ' + ' OR '.join([f'subject:"{kw}"' for kw in self.ACTION_KEYWORDS])
        results = self.service.users().messages().list(userId='me', q=query).execute()
        
        tasks = []
        for msg in results.get('messages', []):
            email = self.service.users().messages().get(userId='me', id=msg['id']).execute()
            tasks.append(self._extract_task(email))
        
        return tasks
    
    def _extract_task(self, email: Dict) -> Dict:
        """Extract task details from email using Gemini API"""
        # Implementation with Gemini
        pass
