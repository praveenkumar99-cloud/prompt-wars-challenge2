"""Module: input_sanitizer.py
Description: Input validation and sanitization utilities.
Author: Praveen Kumar
"""
import logging
import re
from typing import Optional

try:
    import bleach
except ImportError:
    bleach = None

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Service for sanitizing and validating user input."""

    # Allowed HTML tags for rich text (if needed)
    ALLOWED_TAGS: list = []

    # Allowed attributes
    ALLOWED_ATTRIBUTES: dict = {}

    # Maximum message length
    MAX_LENGTH: int = 500

    # Patterns to detect potential injection attacks
    SQL_INJECTION_PATTERN: re.Pattern = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|EXEC|SCRIPT)\b)",
        re.IGNORECASE,
    )

    XSS_PATTERN: re.Pattern = re.compile(
        r"(<script|javascript:|onerror|onload|onclick|<iframe|<object|<embed)",
        re.IGNORECASE,
    )

    def __init__(self) -> None:
        """Initialize InputSanitizer."""
        self._bleach_available: bool = bleach is not None

    def sanitize(self, text: str) -> Optional[str]:
        """Sanitize user input by removing potentially harmful content.

        Args:
            text: Raw user input text.

        Returns:
            Sanitized text or None if input is invalid.
        """
        if not isinstance(text, str):
            logger.warning("Input is not string: %s", type(text))
            return None

        # Check for empty input
        text = text.strip()
        if not text:
            return None

        # Check length
        if len(text) > self.MAX_LENGTH:
            logger.warning(
                "Input exceeds max length: %d > %d",
                len(text),
                self.MAX_LENGTH,
            )
            return None

        # Check for SQL injection patterns
        if self.SQL_INJECTION_PATTERN.search(text):
            logger.warning("Potential SQL injection detected in input")
            return None

        # Check for XSS patterns
        if self.XSS_PATTERN.search(text):
            logger.warning("Potential XSS attack detected in input")
            return None

        # Use bleach if available for HTML sanitization
        if self._bleach_available:
            try:
                text = bleach.clean(
                    text,
                    tags=self.ALLOWED_TAGS,
                    attributes=self.ALLOWED_ATTRIBUTES,
                    strip=True,
                )
            except Exception as e:
                logger.error("Bleach sanitization failed: %s", e)
                return None

        # Remove null bytes
        text = text.replace("\x00", "")

        # Remove control characters except whitespace
        text = "".join(
            char
            for char in text
            if ord(char) >= 32 or char in "\n\r\t"
        )

        # Normalize whitespace
        text = " ".join(text.split())

        return text if text else None

    def validate_session_id(self, session_id: str) -> bool:
        """Validate session ID format.

        Args:
            session_id: Session identifier.

        Returns:
            True if valid, False otherwise.
        """
        if not isinstance(session_id, str):
            return False

        # Allow alphanumeric, hyphens, and underscores only
        return bool(re.match(r"^[a-zA-Z0-9_-]+$", session_id)) and len(
            session_id
        ) <= 128

    def validate_email(self, email: str) -> bool:
        """Validate email address format.

        Args:
            email: Email address.

        Returns:
            True if valid format, False otherwise.
        """
        if not isinstance(email, str):
            return False

        # Simple email validation
        pattern: re.Pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        return bool(pattern.match(email))

    def sanitize_sql_identifier(self, identifier: str) -> Optional[str]:
        """Sanitize SQL identifier (table/column name).

        Args:
            identifier: SQL identifier.

        Returns:
            Sanitized identifier or None.
        """
        if not isinstance(identifier, str):
            return None

        # Allow only alphanumeric and underscore
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
            return None

        return identifier

    def sanitize_url(self, url: str) -> Optional[str]:
        """Sanitize URL to prevent open redirects.

        Args:
            url: URL string.

        Returns:
            Sanitized URL or None if invalid.
        """
        if not isinstance(url, str):
            return None

        url = url.strip()

        # Only allow safe protocols
        safe_protocols: list = ["http://", "https://", "/"]
        if not any(url.startswith(proto) for proto in safe_protocols):
            return None

        # Prevent javascript: protocol
        if "javascript:" in url.lower():
            return None

        return url
