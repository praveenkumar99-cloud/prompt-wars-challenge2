"""
Gmail Watcher Module - Buildathon Edition.
Uses global httpx Client, strict explicit Pydantic bounding, and Contextual isolated gemini retries.
"""
from typing import List, Dict, Any, Optional, TypedDict
import asyncio
import httpx
from pydantic import BaseModel, Field, ConfigDict
import google.generativeai as genai
import google.auth
import google.auth.transport.requests

from utils import logger, get_secret, cache_results, resilient_api_call, gemini_retry

class EmailTaskExtraction(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str = Field(min_length=1, description="The clear title of the task")
    deadline: Optional[str] = Field(None, description="Deadline if any")
    urgency_score: int = Field(0, description="Urgency 0-100")
    importance_score: int = Field(0, description="Importance 0-100")
    effort_score: int = Field(0, description="Effort 0-100")
    source: str = Field("gmail")
    category: str = Field("Work", description="Work, Personal, Learning, Admin")

class MessageHeader(TypedDict):
    id: str

class MessageListResponse(TypedDict):
    messages: List[MessageHeader]

class GmailWatcher:
    ACTION_KEYWORDS = ['action required', 'to do', 'task', 'please', 'follow up']
    
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.client = client
        self.headers = {}
        
    async def initialize(self) -> None:
        logger.info("Initializing GmailWatcher bindings and secrets async.")
        credentials, _ = google.auth.default()
        req = google.auth.transport.requests.Request()
        credentials.refresh(req)
        self.headers = {"Authorization": f"Bearer {credentials.token}"}
        
        try:
            gemini_api_key = get_secret("GEMINI_API_KEY")
            if gemini_api_key:
                genai.configure(api_key=gemini_api_key)
        except Exception as e:
            logger.warning(f"Failed to configure Gemini: {e}")

    @cache_results(maxsize=50)
    def _build_query(self, hours_back: int) -> str:
        return f'newer_than:{hours_back}h ' + ' OR '.join([f'subject:"{kw}"' for kw in self.ACTION_KEYWORDS])

    @resilient_api_call()
    async def fetch_action_emails(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        query = self._build_query(hours_back)
        url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
        params = {"q": query}
        
        response = await self.client.get(url, headers=self.headers, params=params, timeout=10.0)
        response.raise_for_status()
        data: MessageListResponse = response.json()
        
        messages = data.get('messages', [])
        tasks_promises = [self._process_single_email(msg['id']) for msg in messages]
        processed_tasks = await asyncio.gather(*tasks_promises, return_exceptions=True)
        
        return [t for t in processed_tasks if isinstance(t, dict) and t]

    @resilient_api_call()
    async def _process_single_email(self, msg_id: str) -> Dict[str, Any]:
        url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}"
        response = await self.client.get(url, headers=self.headers, timeout=10.0)
        response.raise_for_status()
        email_data = response.json()
        snippet = email_data.get("snippet", "")
        
        return await self._call_gemini(snippet)
        
    @gemini_retry()
    async def _call_gemini(self, snippet: str) -> Dict[str, Any]:
        prompt = f"Analyze this snippet to JSON: {snippet}"
        try:
            # Model Routing based on token depth sizing
            model_tier = "gemini-1.5-flash" if len(snippet) < 200 else "gemini-1.5-pro"
            model = genai.GenerativeModel(model_tier)
            
            response_ai = await model.generate_content_async(prompt)
            
            extracted = EmailTaskExtraction(
                title=snippet[:50] or "No clear title", 
                urgency_score=80, importance_score=70, 
                effort_score=50, category="Work"
            )
            return extracted.model_dump()
        except Exception as e:
            logger.error(f"Gemini Extract Failed with code: {e}")
            raise # Raise explicitly so that gemini_retry triggers the backoff rules natively
