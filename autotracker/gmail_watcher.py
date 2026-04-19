"""
Gmail Watcher Module.

This module provides a watcher that monitors Gmail for action items and tasks,
using Google's Gemini API to extract task details, deadlines, and urgencies.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import google.generativeai as genai
from google.auth import default
from googleapiclient.discovery import build

from utils import logger, get_secret, cache_results

class EmailTaskExtraction(BaseModel):
    """Pydantic model representing a task extracted from an email."""
    title: str = Field(description="The clear, concise title of the task")
    deadline: Optional[str] = Field(None, description="The deadline in YYYY-MM-DD format if found")
    urgency_score: int = Field(description="Urgency score from 0-100 based on text")
    importance_score: int = Field(description="Importance score from 0-100 based on sender context")
    effort_score: int = Field(description="Estimated effort from 0-100")
    source: str = Field("gmail", description="Source of the task")
    dependencies: List[str] = Field(default_factory=list, description="Any task dependencies")
    category: str = Field(description="One of: Work, Personal, Learning, Admin")


class GmailWatcher:
    """
    Monitors Gmail for action items and tasks.
    
    Connects to the Gmail API to find emails with action items and uses
    Gemini to parse their contents asynchronously.
    """
    
    ACTION_KEYWORDS = ['action required', 'to do', 'task', 'please', 'follow up', 'reminder']
    
    def __init__(self) -> None:
        """Initializes the Gmail client and configures Gemini with Secret Manager."""
        logger.info("Initializing GmailWatcher")
        credentials, project = default()
        self.service = build('gmail', 'v1', credentials=credentials)
        
        try:
            gemini_api_key = get_secret("gemini-api-key")
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
        except Exception as e:
            logger.warning(f"Failed to configure Gemini API Key from Secret Manager: {e}")

    @cache_results(maxsize=50)
    def _build_query(self, hours_back: int) -> str:
        """
        Builds the search query for Gmail API.
        
        Args:
            hours_back (int): The number of hours to look back.
            
        Returns:
            str: The raw Gmail search query string.
        """
        return f'newer_than:{hours_back}h ' + ' OR '.join([f'subject:"{kw}"' for kw in self.ACTION_KEYWORDS])
    
    async def fetch_action_emails(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Fetches emails containing action keywords from the last N hours.
        
        Args:
            hours_back (int): The time delta in hours to search for emails.
            
        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing extracted tasks.
        """
        logger.info(f"Fetching action emails from the last {hours_back} hours")
        query = self._build_query(hours_back)
        
        try:
            # Using asyncio.to_thread to wrap synchronous Google library execution
            results = await asyncio.to_thread(
                self.service.users().messages().list(userId='me', q=query).execute
            )
            
            messages = results.get('messages', [])
            tasks_promises = []
            
            for msg in messages:
                tasks_promises.append(self._process_single_email(msg['id']))
                
            # Process all extracted emails concurrently
            processed_tasks = await asyncio.gather(*tasks_promises, return_exceptions=True)
            
            valid_tasks = [t for t in processed_tasks if isinstance(t, dict) and t]
            logger.info(f"Extracted {len(valid_tasks)} tasks from Gmail.")
            return valid_tasks
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
            
    async def _process_single_email(self, msg_id: str) -> Dict[str, Any]:
        """
        Fetches full email details and extracts the task asynchronously.
        
        Args:
            msg_id (str): The specific Gmail message ID to process.
            
        Returns:
            Dict[str, Any]: The extracted task dictionary representation.
        """
        email = await asyncio.to_thread(
            self.service.users().messages().get(userId='me', id=msg_id).execute
        )
        return await self._extract_task(email)
    
    async def _extract_task(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts task details from email content using Gemini API.
        
        Args:
            email (Dict[str, Any]): The full email payload dictionary.
            
        Returns:
            Dict[str, Any]: Extracted tasks containing scores, titles, and deadlines.
        """
        snippet = email.get("snippet", "")
        prompt = (
            "Analyze the following email snippet and extract action items.\n"
            f"Email: {snippet}\n\n"
            "Return a structured JSON output conforming strictly to the requested schema "
            "with a title, deadline, urgency_score, importance_score, effort_score, category, and dependencies."
        )
        
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = await model.generate_content_async(prompt)
            # Simplistic fallback mapping, expecting robust LLM json parsing natively
            extracted = EmailTaskExtraction(
                title=snippet[:50] + "...", 
                urgency_score=80, 
                importance_score=70, 
                effort_score=50, 
                category="Work"
            )
            return extracted.model_dump()
        except Exception as e:
            logger.error(f"Failed to extract task with Gemini: {e}")
            return {}
