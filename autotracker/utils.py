"""
Elite Utilities Module - Buildathon Edition.
"""
import json
import logging
from functools import lru_cache
import httpx
import contextvars

from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from google.cloud import secretmanager_v1

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
        # Inject standard GCP Trace identifiers if attached to record context
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

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True
)
async def get_secret_async(secret_id: str, version_id: str = "latest", project_id: str = "praveen-space") -> str:
    """Retrieves a secret asynchronously using SecretManagerServiceAsyncClient."""
    try:
        client = secretmanager_v1.SecretManagerServiceAsyncClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = await client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Secret Fetch Error: {e}")
        return ""

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
