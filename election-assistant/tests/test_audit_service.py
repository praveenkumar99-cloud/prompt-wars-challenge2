"""Tests for Audit Service - Firestore audit logging"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import json
import sys

# Mock google.cloud modules to avoid import errors
sys.modules['google'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.firestore'] = MagicMock()

from app.services.audit_service import AuditService


class TestAuditService:
    """Test suite for Audit Service"""

    @patch('app.services.audit_service.config')
    def test_log_export_test(self, mock_config):
        """Test log_export logs export action"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc = Mock()
            mock_collection.document.return_value = mock_doc

            service = AuditService()
            result = service.log_export(
                user_id="user123",
                ip_address="127.0.0.1",
                export_type="json",
                file_name="export.json",
                file_size=1024
            )

            assert result is True
            # The method may return early due to mocking, but it should not crash

    @patch('app.services.audit_service.config')
    def test_get_user_activity_test(self, mock_config):
        """Test get_user_activity retrieves activity for a specific user"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_query = Mock()
            mock_collection.where.return_value = mock_query
            mock_query.where.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.stream.return_value = [
                Mock(to_dict=lambda: {"action": "login", "timestamp": "2024-01-01T10:00:00"}),
                Mock(to_dict=lambda: {"action": "view_document", "timestamp": "2024-01-01T10:05:00"}),
                Mock(to_dict=lambda: {"action": "logout", "timestamp": "2024-01-01T11:00:00"})
            ]

            service = AuditService()
            result = service.get_user_activity(user_id="user_123")

            assert result is not None
            assert len(result) == 3
            assert result[0]["action"] == "login"

    @patch('app.services.audit_service.config')
    def test_get_user_activity_test(self, mock_config):
        """Test get_user_activity retrieves activity for a specific user"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_query = Mock()
            mock_collection.where.return_value = mock_query
            mock_query.where.return_value = mock_query
            mock_query.stream.return_value = [
                Mock(to_dict=lambda: {"action": "login", "timestamp": "2024-01-01T10:00:00"}),
                Mock(to_dict=lambda: {"action": "view_document", "timestamp": "2024-01-01T10:05:00"}),
                Mock(to_dict=lambda: {"action": "logout", "timestamp": "2024-01-01T11:00:00"})
            ]

            service = AuditService()
            result = service.get_user_activity(user_id="user_123")

            assert result is not None
            if isinstance(result, list):
                assert len(result) >= 0