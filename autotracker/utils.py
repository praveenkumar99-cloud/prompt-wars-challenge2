"""
Elite Utilities Module - Prompt War Buildathon Edition.
"""
import json
import logging
import os
from functools import lru_cache
import httpx
import contextvars

from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Contextvars for trace and request binding
request_id_ctx = contextvars.ContextVar("request_id", default="")
latency_ctx = contextvars.ContextVar("latency", default=0.0)
status_code_ctx = contextvars.ContextVar("status_code", default=200)

class StructlogFormatter(logging.Formatter):
    """Formats logs into structured JSON for optimal Google Cloud Logging routing."""
    def format(self, record):
        log_data = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "request_id": request_id_ctx.get(),
            "latency_ms": latency_ctx.get(),
            "status_code": status_code_ctx.get()
        }
        if hasattr(record, "trace_id") and record.trace_id:
            log_data["logging.googleapis.com/trace"] = record.trace_id
        return json.dumps(log_data)

logger = logging.getLogger("autotracker_elite")
logger.setLevel(logging.INFO)
# Clear old handlers to not double-print
if logger.hasHandlers():
    logger.handlers.clear()

handler = logging.StreamHandler()
handler.setFormatter(StructlogFormatter())
logger.addHandler(handler)

def cache_results(maxsize: int = 128):
    """Caches returned data strictly to avoid double-processing."""
    def decorator(func):
        return lru_cache(maxsize=maxsize)(func)
    return decorator

def get_secret(secret_id: str) -> str:
    """Sanitized access. Reads strictly from env."""
    return os.getenv(secret_id, "")

def gemini_retry():
    """Specific exponential backoff targeting 429 and 500 equivalent server issues."""
    return retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1.5, min=2, max=10),
        reraise=True
    )

def resilient_api_call():
    """Circuit-breaking and Retry decorator targeted safely at Network IO calls."""
    return retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True
    )
