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

    # Google API Configuration
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")

    # Election Configuration
    ELECTION_COUNTRY: str = os.getenv("ELECTION_COUNTRY", "USA")
    ELECTION_YEAR: int = int(os.getenv("ELECTION_YEAR", "2024"))

    # GCP Project Configuration
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "praveen-space")
    GCP_PROJECT_NUMBER: str = os.getenv("GCP_PROJECT_NUMBER", "665822784067")
    GCP_REGION: str = os.getenv("GCP_REGION", "us-central1")
    CLOUD_RUN_SERVICE_URL: str = os.getenv("CLOUD_RUN_SERVICE_URL", "")

    # Vertex AI Configuration
    VERTEX_AI_LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "us-west1")

    # Firestore Configuration
    FIRESTORE_COLLECTION: str = os.getenv("FIRESTORE_COLLECTION", "chat_sessions")

    # Cloud Storage Configuration
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "")
    GCS_EXPORT_FOLDER: str = os.getenv("GCS_EXPORT_FOLDER", "exports")

    # Cloud Tasks Configuration
    CLOUD_TASKS_QUEUE: str = os.getenv("CLOUD_TASKS_QUEUE", "election-tasks")
    CLOUD_TASKS_SERVICE_ACCOUNT_EMAIL: str = os.getenv(
        "CLOUD_TASKS_SERVICE_ACCOUNT_EMAIL", ""
    )

    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "3600"))

    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # Security Configuration
    API_CORS_ORIGINS: list = os.getenv("API_CORS_ORIGINS", "*").split(",")
    ENABLE_AUDIT_LOGGING: bool = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"

    # Language Configuration
    SUPPORTED_LANGUAGES: list = os.getenv("SUPPORTED_LANGUAGES", "en,es").split(",")
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")

    # Feature Flags
    ENABLE_VERTEX_AI: bool = os.getenv("ENABLE_VERTEX_AI", "true").lower() == "true"
    ENABLE_FIRESTORE: bool = os.getenv("ENABLE_FIRESTORE", "true").lower() == "true"
    ENABLE_CLOUD_STORAGE: bool = os.getenv("ENABLE_CLOUD_STORAGE", "true").lower() == "true"
    ENABLE_CLOUD_TASKS: bool = os.getenv("ENABLE_CLOUD_TASKS", "true").lower() == "true"
    ENABLE_REDIS_CACHE: bool = os.getenv("ENABLE_REDIS_CACHE", "true").lower() == "true"

    # Google Civic API
    CIVIC_API_KEY: Optional[str] = os.getenv("CIVIC_API_KEY")

    @classmethod
    def validate(cls) -> None:
        """Validate configuration on application startup.

        Raises a warning if GOOGLE_API_KEY is not set, indicating
        the application will run in fallback mode.
        """
        if not cls.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY not set — running in fallback mode")
        if cls.ENABLE_CLOUD_STORAGE and not cls.GCS_BUCKET_NAME:
            logger.warning("GCS_BUCKET_NAME not set — Cloud Storage features disabled")
        if cls.ENABLE_FIRESTORE and not cls.GCP_PROJECT_ID:
            logger.warning("GCP_PROJECT_ID not set — Firestore features disabled")


config = Config()
