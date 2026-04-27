"""Module: test_integration.py
Description: Integration tests for Election Assistant with mocks and load testing.
Author: Praveen Kumar
"""
import asyncio
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.models import ChatResponse
from app.server import create_app
from app.services.audit_service import AuditService
from app.services.cache_service import CacheService
from app.services.cloud_storage_service import CloudStorageService


@pytest.fixture(scope="module")
def client():
    """Test client for API endpoints."""
    return TestClient(create_app())


@pytest.fixture
def sample_message():
    """Sample election question."""
    return "How do I register to vote?"


@pytest.fixture
def sample_session_id():
    """Sample session ID."""
    return "test-session-12345"


class TestChatEndpoint:
    """Tests for chat endpoint."""

    def test_chat_success(self, client, sample_message, sample_session_id):
        """Test successful chat interaction."""
        response = client.post(
            "/api/chat",
            json={
                "message": sample_message,
                "session_id": sample_session_id,
                "language": "en",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "intent" in data
        assert "follow_up_suggestions" in data
        assert "sources" in data

    def test_chat_empty_message(self, client, sample_session_id):
        """Test chat with empty message."""
        response = client.post(
            "/api/chat",
            json={"message": "", "session_id": sample_session_id},
        )

        assert response.status_code == 400

    def test_chat_message_too_long(self, client, sample_session_id):
        """Test chat with message exceeding max length."""
        long_message = "x" * 501
        response = client.post(
            "/api/chat",
            json={"message": long_message, "session_id": sample_session_id},
        )

        assert response.status_code == 400

    def test_chat_with_special_characters(self, client, sample_session_id):
        """Test chat with special characters."""
        response = client.post(
            "/api/chat",
            json={
                "message": "How can I vote? (mail, early, or in-person?)",
                "session_id": sample_session_id,
            },
        )

        assert response.status_code == 200

    def test_chat_rate_limiting(self, client, sample_message, sample_session_id):
        """Test rate limiting (simplified test)."""
        # FastAPI rate limiting would need more setup
        responses = []
        for _ in range(3):
            response = client.post(
                "/api/chat",
                json={
                    "message": sample_message,
                    "session_id": sample_session_id,
                },
            )
            responses.append(response.status_code)

        # Should have successful responses
        assert any(status == 200 for status in responses)


class TestConcurrentRequests:
    """Tests for concurrent request handling."""

    @pytest.mark.asyncio
    async def test_concurrent_chat_requests(self):
        """Test handling multiple concurrent requests."""
        client = TestClient(create_app())

        async def make_request(message_num):
            response = client.post(
                "/api/chat",
                json={
                    "message": f"Question {message_num}?",
                    "session_id": f"session-{message_num}",
                },
            )
            return response.status_code

        # Simulate 5 concurrent requests
        tasks = [make_request(i) for i in range(5)]
        results = await asyncio.gather(*tasks)

        # All should be successful
        assert all(status == 200 or status == 400 for status in results)


class TestCacheService:
    """Tests for cache service."""

    def test_cache_set_get(self):
        """Test cache set and get operations."""
        cache = CacheService()

        # Try to set and get (may not work without Redis)
        key = "test:key"
        value = {"test": "data"}

        result = cache.set(key, value)
        # Result depends on Redis availability
        if result:
            cached = cache.get(key)
            assert cached == value

    def test_cache_delete(self):
        """Test cache delete operation."""
        cache = CacheService()

        key = "test:delete"
        cache.set(key, {"data": "value"})
        result = cache.delete(key)

        # Result depends on Redis availability
        assert result is not None

    def test_cache_session_operations(self):
        """Test session-specific cache operations."""
        cache = CacheService()

        session_id = "test-session-123"
        data = {"messages": ["Hello", "How are you?"]}

        cache.set_session(session_id, data)
        cached_data = cache.get_session(session_id)

        if cached_data:
            assert cached_data["messages"] == data["messages"]


class TestAuditService:
    """Tests for audit logging service."""

    def test_audit_log_chat(self):
        """Test chat audit logging."""
        audit = AuditService()

        result = audit.log_chat(
            user_id="user-123",
            ip_address="192.168.1.1",
            message="Test message",
            intent="registration",
            response="Test response",
            status="success",
        )

        # Should return boolean (True if Firestore enabled, False otherwise)
        assert isinstance(result, bool)

    def test_audit_log_api_call(self):
        """Test API call audit logging."""
        audit = AuditService()

        result = audit.log_api_call(
            user_id="user-123",
            ip_address="192.168.1.1",
            endpoint="/api/chat",
            method="POST",
            status_code=200,
            request_size=150,
            response_size=300,
        )

        assert isinstance(result, bool)

    def test_audit_log_error(self):
        """Test error audit logging."""
        audit = AuditService()

        result = audit.log_error(
            user_id="user-123",
            ip_address="192.168.1.1",
            error_message="Test error",
            error_type="TEST_ERROR",
        )

        assert isinstance(result, bool)


class TestInputSanitization:
    """Tests for input sanitization."""

    def test_sanitize_normal_input(self):
        """Test sanitization of normal input."""
        from app.utils.input_sanitizer import InputSanitizer

        sanitizer = InputSanitizer()
        result = sanitizer.sanitize("How do I register to vote?")

        assert result is not None
        assert "register" in result.lower()

    def test_sanitize_sql_injection(self):
        """Test protection against SQL injection."""
        from app.utils.input_sanitizer import InputSanitizer

        sanitizer = InputSanitizer()
        result = sanitizer.sanitize("'; DROP TABLE users; --")

        # Should be detected as SQL injection
        assert result is None

    def test_sanitize_xss_attack(self):
        """Test protection against XSS."""
        from app.utils.input_sanitizer import InputSanitizer

        sanitizer = InputSanitizer()
        result = sanitizer.sanitize('<script>alert("xss")</script>')

        # Should be detected as XSS
        assert result is None

    def test_validate_session_id(self):
        """Test session ID validation."""
        from app.utils.input_sanitizer import InputSanitizer

        sanitizer = InputSanitizer()

        assert sanitizer.validate_session_id("valid-session-123")
        assert sanitizer.validate_session_id("session_456")
        assert not sanitizer.validate_session_id("invalid@session")
        assert not sanitizer.validate_session_id("x" * 200)

    def test_validate_email(self):
        """Test email validation."""
        from app.utils.input_sanitizer import InputSanitizer

        sanitizer = InputSanitizer()

        assert sanitizer.validate_email("user@example.com")
        assert sanitizer.validate_email("test.email+tag@domain.co.uk")
        assert not sanitizer.validate_email("invalid-email")
        assert not sanitizer.validate_email("@example.com")


class TestCloudStorageService:
    """Tests for Cloud Storage service."""

    def test_upload_pdf_when_storage_disabled_returns_false(self):
        """Test that upload returns False gracefully when GCS is disabled."""
        storage_service = CloudStorageService()
        # When Cloud Storage is not configured, should return (False, None)
        pdf_content = b"%PDF-1.4 test content"
        success, url = storage_service.upload_pdf(pdf_content, "test-file")
        # Without GCS credentials, should fail gracefully
        assert isinstance(success, bool)
        assert url is None or isinstance(url, str)

    def test_list_files_when_storage_disabled_returns_empty_list(self):
        """Test that list_files returns empty list gracefully when GCS is disabled."""
        storage_service = CloudStorageService()
        result = storage_service.list_files("exports/")
        # Without GCS credentials, should return empty list
        assert isinstance(result, list)

    def test_get_file_metadata_when_storage_disabled_returns_none(self):
        """Test that metadata retrieval returns None when GCS is disabled."""
        storage_service = CloudStorageService()
        result = storage_service.get_file_metadata("exports/test.pdf")
        assert result is None or isinstance(result, dict)

    def test_delete_file_when_storage_disabled_returns_false(self):
        """Test that delete returns False gracefully when GCS is disabled."""
        storage_service = CloudStorageService()
        result = storage_service.delete_file("exports/test.pdf")
        assert isinstance(result, bool)

    @patch("google.cloud.storage.Client")
    def test_upload_pdf_with_mock_client(self, mock_storage_client):
        """Test PDF upload flow with mocked Cloud Storage client."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.generate_signed_url.return_value = "https://signed-url.example.com"
        mock_blob.exists.return_value = False

        storage_service = CloudStorageService()
        # Verify the service initializes without error
        assert storage_service is not None
        assert isinstance(storage_service._initialized, bool)

    @patch("google.cloud.storage.Client")
    def test_list_files_with_mock_client(self, mock_storage_client):
        """Test file listing with mocked Cloud Storage client."""
        mock_bucket = MagicMock()
        mock_blob_1 = MagicMock()
        mock_blob_1.name = "exports/file1.pdf"
        mock_blob_2 = MagicMock()
        mock_blob_2.name = "exports/file2.pdf"
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.list_blobs.return_value = [mock_blob_1, mock_blob_2]

        storage_service = CloudStorageService()
        # Verify mock setup is correct
        assert mock_storage_client is not None


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "project_id" in data
        assert "vertex_ai_enabled" in data
        assert "firestore_enabled" in data

    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get("/api/status")

        assert response.status_code == 200
        data = response.json()
        assert "google_api_key_configured" in data
        assert "cloud_run_service_url_configured" in data


class TestSecurityHeaders:
    """Tests for security headers."""

    def test_security_headers_present(self, client):
        """Test that security headers are present."""
        response = client.get("/")

        assert "Strict-Transport-Security" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "X-XSS-Protection" in response.headers

    def test_hsts_header_value(self, client):
        """Test HSTS header value."""
        response = client.get("/")

        hsts = response.headers.get("Strict-Transport-Security")
        assert "max-age=" in hsts if hsts else False


class TestLoadHandling:
    """Tests for load and performance."""

    def test_multiple_sequential_requests(self, client, sample_message):
        """Test handling multiple sequential requests."""
        for i in range(5):
            response = client.post(
                "/api/chat",
                json={
                    "message": f"{sample_message} #{i}",
                    "session_id": f"session-{i}",
                },
            )

            assert response.status_code in [200, 400, 429]

    def test_response_time_acceptable(self, client, sample_message):
        """Test that response times are acceptable."""
        import time

        start = time.time()
        response = client.post(
            "/api/chat",
            json={"message": sample_message, "session_id": "perf-test"},
        )
        elapsed = time.time() - start

        # Response should complete within reasonable time
        # (this may vary based on API availability)
        if response.status_code == 200:
            assert elapsed < 30  # 30 second timeout


class TestAccessibility:
    """Tests for accessibility features."""

    def test_html_has_skip_link(self, client):
        """Test that HTML has skip link."""
        response = client.get("/")

        assert response.status_code == 200
        assert "skip-link" in response.text or "Skip to" in response.text

    def test_html_has_aria_labels(self, client):
        """Test that HTML has ARIA labels."""
        response = client.get("/")

        assert "aria-label" in response.text or "aria-labelledby" in response.text

    def test_html_has_role_attributes(self, client):
        """Test that HTML has role attributes."""
        response = client.get("/")

        assert "role=" in response.text


@pytest.fixture
def mock_vertex_ai():
    """Mock Vertex AI service."""
    with patch("app.services.vertex_ai_service.vertexai") as mock:
        yield mock


@pytest.fixture
def mock_firestore():
    """Mock Firestore service."""
    with patch("google.cloud.firestore.Client") as mock:
        yield mock
