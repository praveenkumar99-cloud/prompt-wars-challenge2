"""Module: constants.py
Description: Application-wide constants for magic strings, numbers, and configuration values.
Author: Praveen Kumar
"""

# HTTP Status Codes
HTTP_STATUS_OK = 200
HTTP_STATUS_BAD_REQUEST = 400
HTTP_STATUS_NOT_FOUND = 404
HTTP_STATUS_INTERNAL_SERVER_ERROR = 500

# Message Validation
MAX_MESSAGE_LENGTH = 500
MIN_MESSAGE_LENGTH = 1

# Step IDs
STEP_ID_REGISTER = "register"
STEP_ID_VOTE = "vote"
STEP_ID_MAIL_BALLOT = "mail_ballot"
ALL_STEP_IDS = [STEP_ID_REGISTER, STEP_ID_VOTE, STEP_ID_MAIL_BALLOT]

# Intent Types
INTENT_REGISTRATION = "registration"
INTENT_DEADLINES = "deadlines"
INTENT_VOTING_METHODS = "voting_methods"
INTENT_REQUIREMENTS = "requirements"
INTENT_POLLING_LOCATIONS = "polling_locations"
INTENT_CANDIDATES = "candidates"
INTENT_GENERAL = "general"

ALL_INTENTS = [
    INTENT_REGISTRATION,
    INTENT_DEADLINES,
    INTENT_VOTING_METHODS,
    INTENT_REQUIREMENTS,
    INTENT_POLLING_LOCATIONS,
    INTENT_CANDIDATES,
    INTENT_GENERAL,
]

# Firestore
FIRESTORE_COLLECTION_CHAT_SESSIONS = "chat_sessions"

# Timeline
ELECTION_YEAR_2024 = 2024
PRIMARY_ELECTION_EVENT = "Primary Elections"
GENERAL_ELECTION_EVENT = "General Election"

# Logging Messages
LOG_GCP_LOGGING_INIT = "Google Cloud Logging initialized"
LOG_GCP_LOGGING_FAILED = "Google Cloud Logging initialization failed: %s"
LOG_FIRESTORE_WRITE_FAILED = "Firestore write failed: %s"
LOG_INTENT_CLASSIFICATION_FAILED = "Intent classification failed: %s"
LOG_RESPONSE_GENERATION_FAILED = "Response generation failed: %s"
LOG_GEMINI_INIT_FAILED = "Failed to initialize Gemini: %s"

# Service Status
SERVICE_STATUS_CHECKING = "Checking services"
SERVICE_STATUS_READY = "Ready"
SERVICE_STATUS_ERROR = "Error"
