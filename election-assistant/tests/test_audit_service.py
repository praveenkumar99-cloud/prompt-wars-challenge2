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

    # ==================== log_chat tests ====================

    @patch('app.services.audit_service.config')
    def test_log_chat_success(self, mock_config):
        """Test log_chat successfully logs chat interaction when enabled"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref

            service = AuditService()
            result = service.log_chat(
                user_id="user123",
                ip_address="127.0.0.1",
                message="Hello",
                intent="greeting",
                response="Hi there!"
            )

            assert result is True
            mock_collection.document.assert_called_once()
            mock_doc_ref.set.assert_called_once()

    @patch('app.services.audit_service.config')
    def test_log_chat_disabled_audit_logging(self, mock_config):
        """Test log_chat returns False when ENABLE_AUDIT_LOGGING is False"""
        mock_config.ENABLE_AUDIT_LOGGING = False
        mock_config.ENABLE_FIRESTORE = True

        service = AuditService()
        result = service.log_chat(
            user_id="user123",
            ip_address="127.0.0.1",
            message="Hello",
            intent="greeting",
            response="Hi there!"
        )

        assert result is False

    @patch('app.services.audit_service.config')
    def test_log_chat_disabled_firestore(self, mock_config):
        """Test log_chat returns False when ENABLE_FIRESTORE is False"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = False

        service = AuditService()
        result = service.log_chat(
            user_id="user123",
            ip_address="127.0.0.1",
            message="Hello",
            intent="greeting",
            response="Hi there!"
        )

        assert result is False

    @patch('app.services.audit_service.config')
    def test_log_chat_exception_returns_false(self, mock_config):
        """Test log_chat returns False when Firestore raises exception"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_db.collection.side_effect = Exception("Firestore error")

            service = AuditService()
            result = service.log_chat(
                user_id="user123",
                ip_address="127.0.0.1",
                message="Hello",
                intent="greeting",
                response="Hi there!"
            )

            assert result is False

    @patch('app.services.audit_service.config')
    def test_log_chat_with_metadata(self, mock_config):
        """Test log_chat includes metadata in audit entry"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref

            service = AuditService()
            metadata = {"language": "en", "session_duration": 120}
            result = service.log_chat(
                user_id="user123",
                ip_address="127.0.0.1",
                message="Hello",
                intent="greeting",
                response="Hi there!",
                status="success",
                metadata=metadata
            )

            assert result is True
            call_args = mock_doc_ref.set.call_args[0][0]
            assert "metadata" in call_args
            assert call_args["metadata"] == metadata

    @patch('app.services.audit_service.config')
    def test_log_chat_error_status(self, mock_config):
        """Test log_chat with error status"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref

            service = AuditService()
            result = service.log_chat(
                user_id="user123",
                ip_address="127.0.0.1",
                message="Hello",
                intent="greeting",
                response="Error response",
                status="error"
            )

            assert result is True
            call_args = mock_doc_ref.set.call_args[0][0]
            assert call_args["status"] == "error"

    # ==================== log_api_call tests ====================

    @patch('app.services.audit_service.config')
    def test_log_api_call_success(self, mock_config):
        """Test log_api_call successfully logs API call when enabled"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref

            service = AuditService()
            result = service.log_api_call(
                user_id="user123",
                ip_address="127.0.0.1",
                endpoint="/api/chat",
                method="POST",
                status_code=200,
                request_size=512,
                response_size=1024
            )

            assert result is True
            mock_collection.document.assert_called_once()
            mock_doc_ref.set.assert_called_once()

    @patch('app.services.audit_service.config')
    def test_log_api_call_disabled_audit_logging(self, mock_config):
        """Test log_api_call returns False when ENABLE_AUDIT_LOGGING is False"""
        mock_config.ENABLE_AUDIT_LOGGING = False
        mock_config.ENABLE_FIRESTORE = True

        service = AuditService()
        result = service.log_api_call(
            user_id="user123",
            ip_address="127.0.0.1",
            endpoint="/api/chat",
            method="POST",
            status_code=200
        )

        assert result is False

    @patch('app.services.audit_service.config')
    def test_log_api_call_disabled_firestore(self, mock_config):
        """Test log_api_call returns False when ENABLE_FIRESTORE is False"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = False

        service = AuditService()
        result = service.log_api_call(
            user_id="user123",
            ip_address="127.0.0.1",
            endpoint="/api/chat",
            method="POST",
            status_code=200
        )

        assert result is False

    @patch('app.services.audit_service.config')
    def test_log_api_call_exception_returns_false(self, mock_config):
        """Test log_api_call returns False when Firestore raises exception"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_db.collection.side_effect = Exception("Firestore error")

            service = AuditService()
            result = service.log_api_call(
                user_id="user123",
                ip_address="127.0.0.1",
                endpoint="/api/chat",
                method="POST",
                status_code=200
            )

            assert result is False

    @patch('app.services.audit_service.config')
    def test_log_api_call_error_status(self, mock_config):
        """Test log_api_call sets status='error' for 4xx/5xx status codes"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref

            service = AuditService()
            result = service.log_api_call(
                user_id="user123",
                ip_address="127.0.0.1",
                endpoint="/api/chat",
                method="POST",
                status_code=404
            )

            assert result is True
            call_args = mock_doc_ref.set.call_args[0][0]
            assert call_args["status"] == "error"

    @patch('app.services.audit_service.config')
    def test_log_api_call_success_status(self, mock_config):
        """Test log_api_call sets status='success' for 2xx/3xx status codes"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref

            service = AuditService()
            result = service.log_api_call(
                user_id="user123",
                ip_address="127.0.0.1",
                endpoint="/api/chat",
                method="POST",
                status_code=201
            )

            assert result is True
            call_args = mock_doc_ref.set.call_args[0][0]
            assert call_args["status"] == "success"

    # ==================== log_error tests ====================

    @patch('app.services.audit_service.config')
    def test_log_error_success(self, mock_config):
        """Test log_error successfully logs error event when enabled"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref

            service = AuditService()
            result = service.log_error(
                user_id="user123",
                ip_address="127.0.0.1",
                error_message="Something went wrong",
                error_type="RuntimeError"
            )

            assert result is True
            mock_collection.document.assert_called_once()
            mock_doc_ref.set.assert_called_once()

    @patch('app.services.audit_service.config')
    def test_log_error_disabled_audit_logging(self, mock_config):
        """Test log_error returns False when ENABLE_AUDIT_LOGGING is False"""
        mock_config.ENABLE_AUDIT_LOGGING = False
        mock_config.ENABLE_FIRESTORE = True

        service = AuditService()
        result = service.log_error(
            user_id="user123",
            ip_address="127.0.0.1",
            error_message="Something went wrong",
            error_type="RuntimeError"
        )

        assert result is False

    @patch('app.services.audit_service.config')
    def test_log_error_disabled_firestore(self, mock_config):
        """Test log_error returns False when ENABLE_FIRESTORE is False"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = False

        service = AuditService()
        result = service.log_error(
            user_id="user123",
            ip_address="127.0.0.1",
            error_message="Something went wrong",
            error_type="RuntimeError"
        )

        assert result is False

    @patch('app.services.audit_service.config')
    def test_log_error_exception_returns_false(self, mock_config):
        """Test log_error returns False when Firestore raises exception"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_db.collection.side_effect = Exception("Firestore error")

            service = AuditService()
            result = service.log_error(
                user_id="user123",
                ip_address="127.0.0.1",
                error_message="Something went wrong",
                error_type="RuntimeError"
            )

            assert result is False

    @patch('app.services.audit_service.config')
    def test_log_error_with_endpoint(self, mock_config):
        """Test log_error includes endpoint in audit entry"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref

            service = AuditService()
            result = service.log_error(
                user_id="user123",
                ip_address="127.0.0.1",
                error_message="Something went wrong",
                error_type="RuntimeError",
                endpoint="/api/chat"
            )

            assert result is True
            call_args = mock_doc_ref.set.call_args[0][0]
            assert call_args["endpoint"] == "/api/chat"

    @patch('app.services.audit_service.config')
    def test_log_error_with_metadata(self, mock_config):
        """Test log_error includes custom metadata"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_doc_ref = Mock()
            mock_collection.document.return_value = mock_doc_ref

            service = AuditService()
            metadata = {"stack_trace": "...", "user_agent": "TestAgent"}
            result = service.log_error(
                user_id="user123",
                ip_address="127.0.0.1",
                error_message="Something went wrong",
                error_type="RuntimeError",
                metadata=metadata
            )

            assert result is True
            call_args = mock_doc_ref.set.call_args[0][0]
            assert call_args["metadata"] == metadata

    # ==================== log_export tests ====================

    @patch('app.services.audit_service.config')
    def test_log_export_disabled_audit_logging(self, mock_config):
        """Test log_export returns False when ENABLE_AUDIT_LOGGING is False"""
        mock_config.ENABLE_AUDIT_LOGGING = False
        mock_config.ENABLE_FIRESTORE = True

        service = AuditService()
        result = service.log_export(
            user_id="user123",
            ip_address="127.0.0.1",
            export_type="json",
            file_name="export.json",
            file_size=1024
        )

        assert result is False

    @patch('app.services.audit_service.config')
    def test_log_export_disabled_firestore(self, mock_config):
        """Test log_export returns False when ENABLE_FIRESTORE is False"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = False

        service = AuditService()
        result = service.log_export(
            user_id="user123",
            ip_address="127.0.0.1",
            export_type="json",
            file_name="export.json",
            file_size=1024
        )

        assert result is False

    @patch('app.services.audit_service.config')
    def test_log_export_exception_returns_false(self, mock_config):
        """Test log_export returns False when Firestore raises exception"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_db.collection.side_effect = Exception("Firestore error")

            service = AuditService()
            result = service.log_export(
                user_id="user123",
                ip_address="127.0.0.1",
                export_type="json",
                file_name="export.json",
                file_size=1024
            )

            assert result is False

    # ==================== get_user_activity tests ====================

    @patch('app.services.audit_service.config')
    def test_get_user_activity_empty_result(self, mock_config):
        """Test get_user_activity returns empty list when no logs found"""
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
            mock_query.stream.return_value = []

            service = AuditService()
            result = service.get_user_activity(user_id="user_123")

            assert result == []

    @patch('app.services.audit_service.config')
    def test_get_user_activity_disabled_firestore(self, mock_config):
        """Test get_user_activity returns empty list when FIRESTORE disabled"""
        mock_config.ENABLE_FIRESTORE = False

        service = AuditService()
        result = service.get_user_activity(user_id="user_123")

        assert result == []

    @patch('app.services.audit_service.config')
    def test_get_user_activity_with_limit(self, mock_config):
        """Test get_user_activity respects limit parameter"""
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
                Mock(to_dict=lambda: {"action": "login", "timestamp": "2024-01-01T10:00:00"})
            ]

            service = AuditService()
            result = service.get_user_activity(user_id="user_123", limit=10)

            mock_query.limit.assert_called_once_with(10)
            assert len(result) == 1

    @patch('app.services.audit_service.config')
    def test_get_user_activity_exception_returns_empty(self, mock_config):
        """Test get_user_activity returns empty list on exception"""
        mock_config.ENABLE_AUDIT_LOGGING = True
        mock_config.ENABLE_FIRESTORE = True
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.firestore.Client') as mock_firestore_class:
            mock_db = Mock()
            mock_firestore_class.return_value = mock_db
            mock_collection = Mock()
            mock_db.collection.return_value = mock_collection
            mock_collection.where.side_effect = Exception("Query failed")

            service = AuditService()
            result = service.get_user_activity(user_id="user_123")

            assert result == []
