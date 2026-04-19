from typing import List, Dict
from datetime import datetime
import hashlib
from gmail_watcher import GmailWatcher
from calendar_watcher import CalendarWatcher
from drive_watcher import DriveWatcher

class TaskGenerator:
    """Combines all watchers and generates unified task list"""
    
    def __init__(self):
        self.gmail = GmailWatcher()
        self.calendar = CalendarWatcher()
        self.drive = DriveWatcher()
    
    def generate_tasks(self) -> List[Dict]:
        """Fetch from all sources and generate deduplicated tasks"""
        all_tasks = []
        
        # Fetch from all sources
        all_tasks.extend(self.gmail.fetch_action_emails())
        all_tasks.extend(self.calendar.fetch_upcoming_events())
        all_tasks.extend(self.drive.fetch_recent_changes())
        
        # Deduplicate
        return self._deduplicate_tasks(all_tasks)
    
    def _deduplicate_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Remove duplicate tasks based on title similarity"""
        seen = set()
        unique_tasks = []
        
        for task in tasks:
            task_hash = hashlib.md5(task['title'].lower().encode()).hexdigest()
            if task_hash not in seen:
                seen.add(task_hash)
                unique_tasks.append(task)
        
        return unique_tasks
