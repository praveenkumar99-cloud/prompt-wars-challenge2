"""
Task Generator Module.
"""

import asyncio
import hashlib
from typing import List, Dict, Any
import httpx

from gmail_watcher import GmailWatcher
from calendar_watcher import CalendarWatcher
from drive_watcher import DriveWatcher
from utils import logger, cache_results

class TaskGenerator:
    """
    Combines all watchers executing isolated configs concurrently using `asyncio.gather`.
    """
    
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.gmail = GmailWatcher(client)
        self.calendar = CalendarWatcher(client)
        self.drive = DriveWatcher(client)
    
    async def generate_tasks(self) -> List[Dict[str, Any]]:
        # Execute initialize logic simultaneously across all 3 watchers
        logger.info("Initializing watcher tokens and models concurrently.")
        await asyncio.gather(
            self.gmail.initialize(),
            self.calendar.initialize(),
            self.drive.initialize()
        )
        
        logger.info("Generating tasks from all sources.")
        results = await asyncio.gather(
            self.gmail.fetch_action_emails(),
            self.calendar.fetch_upcoming_events(),
            self.drive.fetch_recent_changes(),
            return_exceptions=True
        )
        
        all_tasks = []
        for result in results:
            if isinstance(result, list):
                all_tasks.extend(result)
            else:
                logger.error(f"Error encountered fetching tasks: {result}")
        
        return self._deduplicate_tasks(all_tasks)
    
    def _calculate_priority(self, task: Dict[str, Any]) -> float:
        u = task.get('urgency_score', 0) * 0.5
        i = task.get('importance_score', 0) * 0.3
        e = task.get('effort_score', 0) * 0.2
        return round(u + i + e, 2)

    @cache_results(maxsize=128)
    def _compute_hash(self, title: str) -> str:
        return hashlib.md5(title.lower().encode()).hexdigest()

    def _deduplicate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        unique_tasks = []
        
        for task in tasks:
            title = task.get('title', '')
            task_hash = self._compute_hash(title)
            
            if task_hash not in seen:
                seen.add(task_hash)
                task['priority'] = self._calculate_priority(task)
                unique_tasks.append(task)
            else:
                pass
                
        unique_tasks.sort(key=lambda x: x.get('priority', 0), reverse=True)
        return unique_tasks
