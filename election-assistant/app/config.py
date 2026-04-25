"""Configuration management"""
import os
from dotenv import load_dotenv
from firebase_admin import credentials, initialize_app, firestore, auth

load_dotenv()


class Config:
    """Application configuration"""
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    ELECTION_COUNTRY = os.getenv("ELECTION_COUNTRY", "USA")
    ELECTION_YEAR = os.getenv("ELECTION_YEAR", "2024")

    # Firebase Configuration
    FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "path/to/firebase/credentials.json")

    # Firebase Authentication Configuration
    ENABLE_ANONYMOUS_AUTH = os.getenv("ENABLE_ANONYMOUS_AUTH", "true").lower() == "true"


config = Config()

# Initialize Firebase Admin SDK
cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)
initialize_app(cred)

# Firestore Client
firestore_client = firestore.client()

# Example: Create anonymous user
if Config.ENABLE_ANONYMOUS_AUTH:
    anonymous_user = auth.create_user()
    print(f"Anonymous user created: {anonymous_user.uid}")
