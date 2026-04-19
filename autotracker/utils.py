"""
Utility module providing Google Cloud integrations and performance wrappers.
Includes Secret Manager for secure secrets access, Cloud Logging for robust logging,
and an lru_cache wrapper utility for efficiency.
"""
from functools import lru_cache
from google.cloud import secretmanager
from google.cloud import logging as cloud_logging
import logging

# Initialize Cloud Logging
try:
    logging_client = cloud_logging.Client()
    logging_client.setup_logging()
except Exception:
    # Fallback for local testing when credentials might not be configured
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("autotracker")

def cache_results(maxsize: int = 128):
    """
    Decorator to cache the results of repetitive utility functions.
    
    Args:
        maxsize (int): The maximum size of the cache. Defaults to 128.
        
    Returns:
        Callable: The decorated function with caching initialized.
    """
    def decorator(func):
        return lru_cache(maxsize=maxsize)(func)
    return decorator

def get_secret(secret_id: str, version_id: str = "latest", project_id: str = "praveen-space") -> str:
    """
    Retrieves a secret from Google Cloud Secret Manager.
    
    Args:
        secret_id (str): The name of the secret.
        version_id (str): The version of the secret to retrieve. Defaults to "latest".
        project_id (str): The Google Cloud project ID. Defaults to "praveen-space".
        
    Returns:
        str: The value of the retrieved secret.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    
    try:
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        logger.info(f"Successfully retrieved secret: {secret_id}")
        return payload
    except Exception as e:
        logger.error(f"Failed to retrieve secret {secret_id}: {str(e)}")
        return "" # returning empty rather than crash for local mock-less testing
