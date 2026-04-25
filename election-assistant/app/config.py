"""Module: config.py
Description: Configuration management using environment variables.
Author: Praveen Kumar
"""
import logging
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Application configuration loaded from environment variables."""

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    ELECTION_COUNTRY: str = os.getenv("ELECTION_COUNTRY", "USA")
    ELECTION_YEAR: int = int(os.getenv("ELECTION_YEAR", "2024"))
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "praveen-space")
    GCP_PROJECT_NUMBER: str = os.getenv("GCP_PROJECT_NUMBER", "665822784067")
    GCP_REGION: str = os.getenv("GCP_REGION", "us-central1")
    CLOUD_RUN_SERVICE_URL: str = os.getenv("CLOUD_RUN_SERVICE_URL", "")
    FIRESTORE_COLLECTION: str = os.getenv("FIRESTORE_COLLECTION", "chat_sessions")

    @classmethod
    def validate(cls) -> None:
        """Validate configuration on application startup.

        Raises a warning if GOOGLE_API_KEY is not set, indicating
        the application will run in fallback mode.
        """
        if not cls.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY not set — running in fallback mode")


config = Config()
