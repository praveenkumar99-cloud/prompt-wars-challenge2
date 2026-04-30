"""Tests for Cloud Storage Service - Google Cloud Storage integration"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock google.cloud.storage to avoid import errors - similar to test_audit_service.py
sys.modules['google'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.storage'] = MagicMock()

from app.services.cloud_storage_service import CloudStorageService


class TestCloudStorageService:
    """Test suite for Cloud Storage Service"""

    @patch('app.services.cloud_storage_service.config')
    def test_upload_pdf_success(self, mock_config):
        """Test successful PDF upload returns signed URL"""
        mock_config.ENABLE_CLOUD_STORAGE = True
        mock_config.GCS_BUCKET_NAME = "test-bucket"
        mock_config.GCP_PROJECT_ID = "test-project"

        with patch('google.cloud.storage.Client') as mock_storage_class:
            mock_client = Mock()
            mock_storage_class.return_value = mock_client
            mock_bucket = Mock()
            mock_client.bucket.return_value = mock_bucket
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            mock_blob.generate_signed_url.return_value = "https://signed-url.example.com"
            mock_blob.upload_from_string.return_value = None

            service = CloudStorageService()
            pdf_bytes = b"fake pdf content" * 100
            success, url = service.upload_pdf(pdf_bytes, "test-file", {"key": "value"})

            assert success is True
            assert url == "https://signed-url.example.com"

    @patch('app.services.cloud_storage_service.config')
    def test_upload_pdf_storage_disabled(self, mock_config):
        """Test upload fails when Cloud Storage is disabled"""
        mock_config.ENABLE_CLOUD_STORAGE = False
        service = CloudStorageService()
        success, url = service.upload_pdf(b"data", "test-file")
        assert success is False
        assert url is None

    @patch('app.services.cloud_storage_service.config')
    def test_upload_pdf_file_too_large(self, mock_config):
        """Test upload fails when PDF exceeds size limit"""
        from app.constants import MAX_PDF_SIZE_MB
        mock_config.ENABLE_CLOUD_STORAGE = True
        mock_config.GCS_BUCKET_NAME = "test-bucket"
        service = CloudStorageService()
        pdf_bytes = b"x" * ((MAX_PDF_SIZE_MB + 1) * 1024 * 1024)
        success, url = service.upload_pdf(pdf_bytes, "test-file")
        assert success is False
        assert url is None

    @patch('app.services.cloud_storage_service.config')
    def test_download_file_success(self, mock_config):
        """Test successful file download"""
        mock_config.ENABLE_CLOUD_STORAGE = True
        mock_config.GCS_BUCKET_NAME = "test-bucket"

        with patch('google.cloud.storage.Client') as mock_storage_class:
            mock_client = Mock()
            mock_storage_class.return_value = mock_client
            mock_bucket = Mock()
            mock_client.bucket.return_value = mock_bucket
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            mock_blob.exists.return_value = True
            mock_blob.download_as_bytes.return_value = b"downloaded content"

            service = CloudStorageService()
            success, content = service.download_file("folder/file.pdf")
            assert success is True
            assert content == b"downloaded content"

    @patch('app.services.cloud_storage_service.config')
    def test_download_file_not_found(self, mock_config):
        """Test download when file doesn't exist"""
        mock_config.ENABLE_CLOUD_STORAGE = True
        mock_config.GCS_BUCKET_NAME = "test-bucket"

        with patch('google.cloud.storage.Client') as mock_storage_class:
            mock_client = Mock()
            mock_storage_class.return_value = mock_client
            mock_bucket = Mock()
            mock_client.bucket.return_value = mock_bucket
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            mock_blob.exists.return_value = False

            service = CloudStorageService()
            success, content = service.download_file("nonexistent.pdf")
            assert success is False
            assert content is None

    @patch('app.services.cloud_storage_service.config')
    def test_download_file_storage_disabled(self, mock_config):
        """Test download fails when Cloud Storage is disabled"""
        mock_config.ENABLE_CLOUD_STORAGE = False
        service = CloudStorageService()
        success, content = service.download_file("file.pdf")
        assert success is False
        assert content is None

    @patch('app.services.cloud_storage_service.config')
    def test_delete_file_success(self, mock_config):
        """Test successful file deletion"""
        mock_config.ENABLE_CLOUD_STORAGE = True
        mock_config.GCS_BUCKET_NAME = "test-bucket"

        with patch('google.cloud.storage.Client') as mock_storage_class:
            mock_client = Mock()
            mock_storage_class.return_value = mock_client
            mock_bucket = Mock()
            mock_client.bucket.return_value = mock_bucket
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob

            service = CloudStorageService()
            result = service.delete_file("folder/file.pdf")
            assert result is True
            mock_blob.delete.assert_called_once()

    @patch('app.services.cloud_storage_service.config')
    def test_delete_file_storage_disabled(self, mock_config):
        """Test delete fails when Cloud Storage is disabled"""
        mock_config.ENABLE_CLOUD_STORAGE = False
        service = CloudStorageService()
        result = service.delete_file("file.pdf")
        assert result is False

    @patch('app.services.cloud_storage_service.config')
    def test_list_files_success(self, mock_config):
        """Test listing files with prefix"""
        mock_config.ENABLE_CLOUD_STORAGE = True
        mock_config.GCS_BUCKET_NAME = "test-bucket"

        with patch('google.cloud.storage.Client') as mock_storage_class:
            mock_client = Mock()
            mock_storage_class.return_value = mock_client
            mock_bucket = Mock()
            mock_client.bucket.return_value = mock_bucket
            mock_blob1 = Mock()
            mock_blob1.name = "exports/file1.pdf"
            mock_blob2 = Mock()
            mock_blob2.name = "exports/file2.pdf"
            mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]

            service = CloudStorageService()
            files = service.list_files("exports/")
            assert len(files) == 2
            assert "exports/file1.pdf" in files
            assert "exports/file2.pdf" in files

    @patch('app.services.cloud_storage_service.config')
    def test_list_files_storage_disabled(self, mock_config):
        """Test list files returns empty when storage disabled"""
        mock_config.ENABLE_CLOUD_STORAGE = False
        service = CloudStorageService()
        files = service.list_files("any/")
        assert files == []

    @patch('app.services.cloud_storage_service.config')
    def test_get_file_metadata_success(self, mock_config):
        """Test retrieving file metadata"""
        mock_config.ENABLE_CLOUD_STORAGE = True
        mock_config.GCS_BUCKET_NAME = "test-bucket"

        with patch('google.cloud.storage.Client') as mock_storage_class:
            mock_client = Mock()
            mock_storage_class.return_value = mock_client
            mock_bucket = Mock()
            mock_client.bucket.return_value = mock_bucket
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            mock_blob.exists.return_value = True
            mock_blob.name = "file.pdf"
            mock_blob.size = 1024
            mock_blob.content_type = "application/pdf"
            mock_blob.time_created = "2024-01-01T00:00:00"
            mock_blob.updated = "2024-01-01T00:00:00"
            mock_blob.metadata = {"key": "value"}

            service = CloudStorageService()
            metadata = service.get_file_metadata("file.pdf")
            assert metadata is not None
            assert metadata["name"] == "file.pdf"
            assert metadata["size"] == 1024
            assert metadata["content_type"] == "application/pdf"
            assert metadata["metadata"] == {"key": "value"}

    @patch('app.services.cloud_storage_service.config')
    def test_get_file_metadata_not_found(self, mock_config):
        """Test metadata retrieval for non-existent file"""
        mock_config.ENABLE_CLOUD_STORAGE = True
        mock_config.GCS_BUCKET_NAME = "test-bucket"

        with patch('google.cloud.storage.Client') as mock_storage_class:
            mock_client = Mock()
            mock_storage_class.return_value = mock_client
            mock_bucket = Mock()
            mock_client.bucket.return_value = mock_bucket
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            mock_blob.exists.return_value = False

            service = CloudStorageService()
            metadata = service.get_file_metadata("nonexistent.pdf")
            assert metadata is None

    @patch('app.services.cloud_storage_service.config')
    def test_get_file_metadata_storage_disabled(self, mock_config):
        """Test metadata retrieval when storage is disabled"""
        mock_config.ENABLE_CLOUD_STORAGE = False
        service = CloudStorageService()
        metadata = service.get_file_metadata("file.pdf")
        assert metadata is None

    @patch('app.services.cloud_storage_service.config')
    def test_generate_signed_url_success(self, mock_config):
        """Test generating signed URL"""
        mock_config.ENABLE_CLOUD_STORAGE = True
        mock_config.GCS_BUCKET_NAME = "test-bucket"

        with patch('google.cloud.storage.Client') as mock_storage_class:
            mock_client = Mock()
            mock_storage_class.return_value = mock_client
            mock_bucket = Mock()
            mock_client.bucket.return_value = mock_bucket
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            mock_blob.generate_signed_url.return_value = "https://signed-url.example.com"

            service = CloudStorageService()
            url = service.generate_signed_url("file.pdf", expiration_hours=12)
            assert url == "https://signed-url.example.com"

    @patch('app.services.cloud_storage_service.config')
    def test_generate_signed_url_storage_disabled(self, mock_config):
        """Test signed URL generation when storage is disabled"""
        mock_config.ENABLE_CLOUD_STORAGE = False
        service = CloudStorageService()
        url = service.generate_signed_url("file.pdf")
        assert url is None
