"""Module: constants.py
Description: Application-wide constants for magic strings, numbers, and configuration values.
Author: Praveen Kumar
"""

# HTTP Status Codes
HTTP_STATUS_OK: int = 200
HTTP_STATUS_CREATED: int = 201
HTTP_STATUS_BAD_REQUEST: int = 400
HTTP_STATUS_UNAUTHORIZED: int = 401
HTTP_STATUS_FORBIDDEN: int = 403
HTTP_STATUS_NOT_FOUND: int = 404
HTTP_STATUS_RATE_LIMIT: int = 429
HTTP_STATUS_INTERNAL_SERVER_ERROR: int = 500
HTTP_STATUS_SERVICE_UNAVAILABLE: int = 503

# Message Validation
MAX_MESSAGE_LENGTH: int = 500
MIN_MESSAGE_LENGTH: int = 1
MAX_SESSION_HISTORY: int = 100

# Step IDs
STEP_ID_REGISTER: str = "register"
STEP_ID_VOTE: str = "vote"
STEP_ID_MAIL_BALLOT: str = "mail_ballot"
ALL_STEP_IDS: list = [STEP_ID_REGISTER, STEP_ID_VOTE, STEP_ID_MAIL_BALLOT]

# Intent Types
INTENT_REGISTRATION: str = "registration"
INTENT_DEADLINES: str = "deadlines"
INTENT_VOTING_METHODS: str = "voting_methods"
INTENT_REQUIREMENTS: str = "requirements"
INTENT_POLLING_LOCATIONS: str = "polling_locations"
INTENT_CANDIDATES: str = "candidates"
INTENT_GENERAL: str = "general"

ALL_INTENTS: list = [
    INTENT_REGISTRATION,
    INTENT_DEADLINES,
    INTENT_VOTING_METHODS,
    INTENT_REQUIREMENTS,
    INTENT_POLLING_LOCATIONS,
    INTENT_CANDIDATES,
    INTENT_GENERAL,
]

# Firestore Collections
FIRESTORE_COLLECTION_CHAT_SESSIONS: str = "chat_sessions"
FIRESTORE_COLLECTION_AUDIT_LOGS: str = "audit_logs"
FIRESTORE_FIELD_TIMESTAMP: str = "timestamp"
FIRESTORE_FIELD_MESSAGE: str = "message"
FIRESTORE_FIELD_INTENT: str = "intent"
FIRESTORE_FIELD_RESPONSE: str = "response"
FIRESTORE_FIELD_USER_ID: str = "user_id"
FIRESTORE_FIELD_IP_ADDRESS: str = "ip_address"
FIRESTORE_FIELD_ACTION: str = "action"
FIRESTORE_FIELD_STATUS: str = "status"

# Timeline Events
ELECTION_YEAR_2024: int = 2024
PRIMARY_ELECTION_EVENT: str = "Primary Elections"
GENERAL_ELECTION_EVENT: str = "General Election"
REGISTRATION_DEADLINE: str = "registration_deadline"
EARLY_VOTING_START: str = "early_voting_start"
EARLY_VOTING_END: str = "early_voting_end"
ELECTION_DAY: str = "election_day"
MAIL_BALLOT_DEADLINE: str = "mail_ballot_deadline"

# Logging Messages
LOG_GCP_LOGGING_INIT: str = "Google Cloud Logging initialized"
LOG_GCP_LOGGING_FAILED: str = "Google Cloud Logging initialization failed: %s"
LOG_VERTEX_AI_INIT: str = "Vertex AI initialized"
LOG_VERTEX_AI_FAILED: str = "Vertex AI initialization failed: %s"
LOG_FIRESTORE_WRITE_FAILED: str = "Firestore write failed: %s"
LOG_INTENT_CLASSIFICATION_FAILED: str = "Intent classification failed: %s"
LOG_RESPONSE_GENERATION_FAILED: str = "Response generation failed: %s"
LOG_GEMINI_INIT_FAILED: str = "Failed to initialize Gemini: %s"
LOG_RATE_LIMIT_EXCEEDED: str = "Rate limit exceeded for IP: %s"
LOG_INPUT_SANITIZATION_FAILED: str = "Input sanitization failed: %s"
LOG_AUDIT_LOG_FAILED: str = "Audit logging failed: %s"

# Service Status
SERVICE_STATUS_CHECKING: str = "Checking services"
SERVICE_STATUS_READY: str = "Ready"
SERVICE_STATUS_ERROR: str = "Error"

# Cache Keys
CACHE_KEY_SESSION: str = "session:%s"
CACHE_KEY_INTENT: str = "intent:%s"
CACHE_KEY_TIMELINE: str = "timeline:%s"
CACHE_TTL_SHORT: int = 300  # 5 minutes
CACHE_TTL_MEDIUM: int = 3600  # 1 hour
CACHE_TTL_LONG: int = 86400  # 24 hours

# Security
SECURITY_HEADER_HSTS: str = "max-age=31536000; includeSubDomains"
SECURITY_HEADER_X_FRAME_OPTIONS: str = "DENY"
SECURITY_HEADER_X_CONTENT_TYPE_OPTIONS: str = "nosniff"
SECURITY_HEADER_X_XSS_PROTECTION: str = "1; mode=block"
SECURITY_HEADER_REFERRER_POLICY: str = "strict-origin-when-cross-origin"
SECURITY_HEADER_PERMISSIONS_POLICY: str = "geolocation=(), microphone=(), camera=()"

# Language Codes
LANGUAGE_ENGLISH: str = "en"
LANGUAGE_SPANISH: str = "es"
SUPPORTED_LANGUAGE_CODES: list = [LANGUAGE_ENGLISH, LANGUAGE_SPANISH]

# PDF Export
PDF_EXPORT_FOLDER: str = "election_guides"
PDF_EXPORT_EXTENSION: str = ".pdf"
MAX_PDF_SIZE_MB: int = 10

# Audit Actions
AUDIT_ACTION_CHAT: str = "CHAT"
AUDIT_ACTION_LOGIN: str = "LOGIN"
AUDIT_ACTION_EXPORT: str = "EXPORT"
AUDIT_ACTION_API_CALL: str = "API_CALL"
AUDIT_ACTION_ERROR: str = "ERROR"

# Feature IDs
FEATURE_VOICE_INPUT: str = "voice_input"
FEATURE_PDF_EXPORT: str = "pdf_export"
FEATURE_ACCESSIBILITY: str = "accessibility"
FEATURE_MULTI_LANGUAGE: str = "multi_language"
