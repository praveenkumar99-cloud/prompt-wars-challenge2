"""
Task Generator Module.

This module orchestrates fetching from Gmail, Calendar, and Drive Watchers
concurrently using asyncio and deduplicates generated tasks.
"""

import asyncio
import hashlib
from typing import List, Dict, Any

from gmail_watcher import GmailWatcher
from calendar_watcher import CalendarWatcher
from drive_watcher import DriveWatcher
from utils import logger, cache_results

class TaskGenerator:
    """
    Combines all watchers and generates a unified, prioritized task list.
    """
    
    def __init__(self) -> None:
        """Initializes all required watchers."""
        logger.info("Initializing TaskGenerator")
        self.gmail = GmailWatcher()
        self.calendar = CalendarWatcher()
        self.drive = DriveWatcher()
    
    async def generate_tasks(self) -> List[Dict[str, Any]]:
        """
        Fetch tasks from all sources concurrently and deduplicate gracefully.
        
        Returns:
            List[Dict[str, Any]]: List of unified tasks.
        """
        logger.info("Generating tasks from all sources concurrently")
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
        """
        Task scoring algorithm computing overall priority.
        Priority = (Urgency x 0.5) + (Importance x 0.3) + (Effort x 0.2)
        """
        u = task.get('urgency_score', 0) * 0.5
        i = task.get('importance_score', 0) * 0.3
        e = task.get('effort_score', 0) * 0.2
        return round(u + i + e, 2)

    @cache_results(maxsize=128)
    def _compute_hash(self, title: str) -> str:
        """Computes md5 hash for deduplication strategy."""
        return hashlib.md5(title.lower().encode()).hexdigest()

    def _deduplicate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Removes duplicate tasks based on title similarity natively.
        
        Args:
            tasks (List[Dict[str, Any]]): Unfiltered tasks.
            
        Returns:
            List[Dict[str, Any]]: Unique, deduplicated tasks.
        """
        seen = set()
        unique_tasks = []
        
        for task in tasks:
            title = task.get('title', '')
            task_hash = self._compute_hash(title)
            
            if task_hash not in seen:
                seen.add(task_hash)
                # Compute and attach the priority while deduplicating
                task['priority'] = self._calculate_priority(task)
                unique_tasks.append(task)
            else:
                logger.info(f"Filtered duplicate task: {title}")
                
        # Sort by priority
        unique_tasks.sort(key=lambda x: x.get('priority', 0), reverse=True)
        return unique_tasks
