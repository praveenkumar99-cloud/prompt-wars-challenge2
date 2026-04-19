"""
Elite Utilities Module.
"""
from functools import lru_cache
import logging
import json
from google.cloud import secretmanager
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import httpx

class StructlogFormatter(logging.Formatter):
    """Formats logs into structured JSON for optimal Google Cloud Logging routing."""
    def format(self, record):
        log_data = {
            "severity": record.levelname,
            "message": record.getMessage(),
            "name": record.name
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
def get_secret(secret_id: str, version_id: str = "latest", project_id: str = "praveen-space") -> str:
    """Retrieves a secret synchronously with built-in retry reliability."""
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        logger.error(f"Secret Fetch Error: {e}")
        return ""

def resilient_api_call():
    """Circuit-breaking and Retry decorator targeted safely at Network IO calls."""
    return retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException)),
        reraise=True
    )
