"""Configuration management."""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    ELECTION_COUNTRY = os.getenv("ELECTION_COUNTRY", "USA")
    ELECTION_YEAR = os.getenv("ELECTION_YEAR", "2024")
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "praveen-space")
    GCP_PROJECT_NUMBER = os.getenv("GCP_PROJECT_NUMBER", "665822784067")
    GCP_REGION = os.getenv("GCP_REGION", "us-central1")
    CLOUD_RUN_SERVICE_URL = os.getenv("CLOUD_RUN_SERVICE_URL", "")


config = Config()
