"""Module: audit_service.py
Description: Audit logging service for compliance and tracking.
Author: Praveen Kumar
"""
__all__ = ["AuditService"]

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from ..config import config

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging to Firestore."""

    def __init__(self) -> None:
        """Initialize AuditService."""
        self._firestore_available: bool = config.ENABLE_FIRESTORE

    def log_chat(
        self,
        user_id: str,
        ip_address: str,
        message: str,
        intent: str,
        response: str,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log chat interaction to Firestore.

        Args:
            user_id: User or session ID.
            ip_address: Client IP address.
            message: User's message.
            intent: Classified intent.
            response: Assistant's response.
            status: Success/failure status.
            metadata: Additional metadata.

        Returns:
            True if logged successfully.
        """
        if not self._firestore_available or not config.ENABLE_AUDIT_LOGGING:
            return False

        try:
            from google.cloud import firestore

            db = firestore.Client(project=config.GCP_PROJECT_ID)

            audit_entry = {
                FIRESTORE_FIELD_ACTION: AUDIT_ACTION_CHAT,
                FIRESTORE_FIELD_USER_ID: user_id,
                FIRESTORE_FIELD_IP_ADDRESS: ip_address,
                FIRESTORE_FIELD_MESSAGE: message,
                "intent": intent,
                "response": response,
                FIRESTORE_FIELD_STATUS: status,
                FIRESTORE_FIELD_TIMESTAMP: firestore.SERVER_TIMESTAMP,
                "metadata": metadata or {},
            }

            db.collection(FIRESTORE_COLLECTION_AUDIT_LOGS).add(audit_entry)
            logger.info(
                "Chat audit logged: user=%s, intent=%s, status=%s",
                user_id,
                intent,
                status,
            )
            return True

        except Exception as e:
            logger.error("Audit logging failed: %s", e)
            return False

    def log_api_call(
        self,
        user_id: str,
        ip_address: str,
        endpoint: str,
        method: str,
        status_code: int,
        request_size: int = 0,
        response_size: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log API call to Firestore.

        Args:
            user_id: User or session ID.
            ip_address: Client IP address.
            endpoint: API endpoint.
            method: HTTP method.
            status_code: Response status code.
            request_size: Request payload size.
            response_size: Response payload size.
            metadata: Additional metadata.

        Returns:
            True if logged successfully.
        """
        if not self._firestore_available or not config.ENABLE_AUDIT_LOGGING:
            return False

        try:
            from google.cloud import firestore

            db = firestore.Client(project=config.GCP_PROJECT_ID)

            status = "success" if status_code < 400 else "error"

            audit_entry = {
                FIRESTORE_FIELD_ACTION: AUDIT_ACTION_API_CALL,
                FIRESTORE_FIELD_USER_ID: user_id,
                FIRESTORE_FIELD_IP_ADDRESS: ip_address,
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "request_size": request_size,
                "response_size": response_size,
                FIRESTORE_FIELD_STATUS: status,
                FIRESTORE_FIELD_TIMESTAMP: firestore.SERVER_TIMESTAMP,
                "metadata": metadata or {},
            }

            db.collection(FIRESTORE_COLLECTION_AUDIT_LOGS).add(audit_entry)
            logger.debug(
                "API call logged: %s %s from %s, status=%d",
                method,
                endpoint,
                ip_address,
                status_code,
            )
            return True

        except Exception as e:
            logger.error("API audit logging failed: %s", e)
            return False

    def log_error(
        self,
        user_id: str,
        ip_address: str,
        error_message: str,
        error_type: str,
        endpoint: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log error event to Firestore.

        Args:
            user_id: User or session ID.
            ip_address: Client IP address.
            error_message: Error message.
            error_type: Type of error.
            endpoint: Optional endpoint where error occurred.
            metadata: Additional metadata.

        Returns:
            True if logged successfully.
        """
        if not self._firestore_available or not config.ENABLE_AUDIT_LOGGING:
            return False

        try:
            from google.cloud import firestore

            db = firestore.Client(project=config.GCP_PROJECT_ID)

            audit_entry = {
                FIRESTORE_FIELD_ACTION: AUDIT_ACTION_ERROR,
                FIRESTORE_FIELD_USER_ID: user_id,
                FIRESTORE_FIELD_IP_ADDRESS: ip_address,
                "error_message": error_message,
                "error_type": error_type,
                "endpoint": endpoint,
                FIRESTORE_FIELD_STATUS: "error",
                FIRESTORE_FIELD_TIMESTAMP: firestore.SERVER_TIMESTAMP,
                "metadata": metadata or {},
            }

            db.collection(FIRESTORE_COLLECTION_AUDIT_LOGS).add(audit_entry)
            logger.warning(
                "Error logged: %s (%s) from %s", error_message, error_type, ip_address
            )
            return True

        except Exception as e:
            logger.error("Error audit logging failed: %s", e)
            return False

    def log_export(
        self,
        user_id: str,
        ip_address: str,
        export_type: str,
        file_name: str,
        file_size: int,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Log export action to Firestore.

        Args:
            user_id: User or session ID.
            ip_address: Client IP address.
            export_type: Type of export (PDF, CSV, etc.).
            file_name: Exported file name.
            file_size: File size in bytes.
            status: Success/failure status.
            metadata: Additional metadata.

        Returns:
            True if logged successfully.
        """
        if not self._firestore_available or not config.ENABLE_AUDIT_LOGGING:
            return False

        try:
            from google.cloud import firestore

            db = firestore.Client(project=config.GCP_PROJECT_ID)

            audit_entry = {
                FIRESTORE_FIELD_ACTION: AUDIT_ACTION_EXPORT,
                FIRESTORE_FIELD_USER_ID: user_id,
                FIRESTORE_FIELD_IP_ADDRESS: ip_address,
                "export_type": export_type,
                "file_name": file_name,
                "file_size": file_size,
                FIRESTORE_FIELD_STATUS: status,
                FIRESTORE_FIELD_TIMESTAMP: firestore.SERVER_TIMESTAMP,
                "metadata": metadata or {},
            }

            db.collection(FIRESTORE_COLLECTION_AUDIT_LOGS).add(audit_entry)
            logger.info(
                "Export logged: %s (%s) from %s, size=%d bytes",
                file_name,
                export_type,
                ip_address,
                file_size,
            )
            return True

        except Exception as e:
            logger.error("Export audit logging failed: %s", e)
            return False

    def get_user_activity(
        self, user_id: str, limit: int = 100
    ) -> list:
        """Retrieve user activity logs from Firestore.

        Args:
            user_id: User or session ID.
            limit: Maximum number of records to return.

        Returns:
            List of audit log entries.
        """
        if not self._firestore_available:
            return []

        try:
            from google.cloud import firestore

            db = firestore.Client(project=config.GCP_PROJECT_ID)

            docs = (
                db.collection(FIRESTORE_COLLECTION_AUDIT_LOGS)
                .where(FIRESTORE_FIELD_USER_ID, "==", user_id)
                .order_by(FIRESTORE_FIELD_TIMESTAMP, direction="DESCENDING")
                .limit(limit)
                .stream()
            )

            return [doc.to_dict() for doc in docs]

        except Exception as e:
            logger.error("Activity retrieval failed: %s", e)
            return []
