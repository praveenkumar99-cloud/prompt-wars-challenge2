"""Module: cloud_storage_service.py
Description: Google Cloud Storage integration for file uploads and exports.
Author: Praveen Kumar
"""
import io
import logging
from datetime import timedelta
from typing import Optional, Tuple

from ..config import config
from ..constants import MAX_PDF_SIZE_MB, PDF_EXPORT_EXTENSION, PDF_EXPORT_FOLDER

logger = logging.getLogger(__name__)


class CloudStorageService:
    """Service for managing files in Google Cloud Storage."""

    def __init__(self) -> None:
        """Initialize CloudStorageService with lazy client initialization."""
        self._client: Optional[object] = None
        self._initialized: bool = False

    def _get_client(self) -> Optional[object]:
        """Get or create Cloud Storage client.

        Returns:
            GCS client instance or None if disabled/failed.
        """
        if self._initialized:
            return self._client

        if not config.ENABLE_CLOUD_STORAGE or not config.GCS_BUCKET_NAME:
            self._initialized = True
            return None

        try:
            from google.cloud import storage

            self._client = storage.Client(project=config.GCP_PROJECT_ID)
            logger.info("Cloud Storage client initialized")
            self._initialized = True
            return self._client
        except Exception as e:
            logger.warning(
                "Cloud Storage initialization failed, feature disabled: %s", e
            )
            self._initialized = True
            return None

    def upload_pdf(
        self, pdf_content: bytes, filename: str, metadata: Optional[dict] = None
    ) -> Tuple[bool, Optional[str]]:
        """Upload PDF file to Cloud Storage.

        Args:
            pdf_content: PDF file bytes.
            filename: Name for the file (without extension).
            metadata: Optional file metadata.

        Returns:
            Tuple of (success: bool, signed_url: Optional[str]).
        """
        try:
            client = self._get_client()
            if not client:
                return False, None

            # Validate file size
            size_mb = len(pdf_content) / (1024 * 1024)
            if size_mb > MAX_PDF_SIZE_MB:
                logger.warning(
                    "PDF exceeds max size: %.2f MB > %d MB",
                    size_mb,
                    MAX_PDF_SIZE_MB,
                )
                return False, None

            bucket = client.bucket(config.GCS_BUCKET_NAME)
            blob_name = "%s/%s%s" % (PDF_EXPORT_FOLDER, filename, PDF_EXPORT_EXTENSION)
            blob = bucket.blob(blob_name)

            # Set metadata
            if metadata:
                blob.metadata = metadata

            blob.upload_from_string(
                pdf_content, content_type="application/pdf"
            )

            # Generate signed URL valid for 24 hours
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=24),
                method="GET",
            )

            logger.info("PDF uploaded successfully: %s", blob_name)
            return True, signed_url

        except Exception as e:
            logger.error("PDF upload failed: %s", e)
            return False, None

    def download_file(self, blob_name: str) -> Tuple[bool, Optional[bytes]]:
        """Download file from Cloud Storage.

        Args:
            blob_name: Full path to blob in bucket.

        Returns:
            Tuple of (success: bool, content: Optional[bytes]).
        """
        try:
            client = self._get_client()
            if not client:
                return False, None

            bucket = client.bucket(config.GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)

            if not blob.exists():
                logger.warning("Blob not found: %s", blob_name)
                return False, None

            content = blob.download_as_bytes()
            return True, content

        except Exception as e:
            logger.error("File download failed for %s: %s", blob_name, e)
            return False, None

    def delete_file(self, blob_name: str) -> bool:
        """Delete file from Cloud Storage.

        Args:
            blob_name: Full path to blob in bucket.

        Returns:
            True if successful, False otherwise.
        """
        try:
            client = self._get_client()
            if not client:
                return False

            bucket = client.bucket(config.GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)
            blob.delete()

            logger.info("File deleted: %s", blob_name)
            return True

        except Exception as e:
            logger.error("File deletion failed for %s: %s", blob_name, e)
            return False

    def list_files(self, prefix: str = "") -> list:
        """List files in bucket with optional prefix filter.

        Args:
            prefix: Optional prefix to filter files.

        Returns:
            List of blob names.
        """
        try:
            client = self._get_client()
            if not client:
                return []

            bucket = client.bucket(config.GCS_BUCKET_NAME)
            blobs = bucket.list_blobs(prefix=prefix)

            return [blob.name for blob in blobs]

        except Exception as e:
            logger.error("File listing failed: %s", e)
            return []

    def get_file_metadata(self, blob_name: str) -> Optional[dict]:
        """Get file metadata from Cloud Storage.

        Args:
            blob_name: Full path to blob in bucket.

        Returns:
            Dictionary with metadata or None.
        """
        try:
            client = self._get_client()
            if not client:
                return None

            bucket = client.bucket(config.GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)

            if not blob.exists():
                return None

            return {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created,
                "updated": blob.updated,
                "metadata": blob.metadata or {},
            }

        except Exception as e:
            logger.error("Metadata retrieval failed for %s: %s", blob_name, e)
            return None

    def generate_signed_url(
        self, blob_name: str, expiration_hours: int = 24
    ) -> Optional[str]:
        """Generate signed URL for a file.

        Args:
            blob_name: Full path to blob in bucket.
            expiration_hours: URL expiration time in hours.

        Returns:
            Signed URL string or None.
        """
        try:
            client = self._get_client()
            if not client:
                return None

            bucket = client.bucket(config.GCS_BUCKET_NAME)
            blob = bucket.blob(blob_name)

            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=expiration_hours),
                method="GET",
            )

            return signed_url

        except Exception as e:
            logger.error("Signed URL generation failed for %s: %s", blob_name, e)
            return None
