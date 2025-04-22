"""Storage module for handling file operations with Minio."""

import os
from typing import BinaryIO, Optional, Tuple
from minio import Minio
from minio.error import S3Error

from app.config import settings


class MinioStorage:
    """Minio storage handler."""

    def __init__(
        self,
        minio_url: str = settings.MINIO_URL,
        access_key: str = settings.MINIO_ROOT_USER,
        secret_key: str = settings.MINIO_ROOT_PASSWORD,
        bucket_name: str = settings.MINIO_BUCKET,
        secure: bool = False,
    ):
        """Initialize Minio client.

        Args:
            minio_url: Minio server URL
            access_key: Access key
            secret_key: Secret key
            bucket_name: Bucket name
            secure: Use HTTPS
        """
        self.client = Minio(
            minio_url,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )
        self.bucket_name = bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Ensure the bucket exists, create it otherwise."""
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except S3Error as e:
            raise RuntimeError(f"Failed to create or check bucket: {e}")

    def upload_file(
        self, file_obj: BinaryIO, object_name: str, content_type: Optional[str] = None
    ) -> str:
        """Upload file to Minio.

        Args:
            file_obj: File object
            object_name: Object name in storage
            content_type: Content type of the file

        Returns:
            str: Object path in storage
        """
        try:
            # Get file size
            file_obj.seek(0, os.SEEK_END)
            file_size = file_obj.tell()
            file_obj.seek(0)

            # Upload file
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_obj,
                length=file_size,
                content_type=content_type,
            )
            return object_name
        except S3Error as e:
            raise RuntimeError(f"Failed to upload file: {e}")

    def download_file(self, object_name: str) -> Tuple[BinaryIO, str]:
        """Download file from Minio.

        Args:
            object_name: Object name in storage

        Returns:
            Tuple[BinaryIO, str]: File object and content type
        """
        try:
            response = self.client.get_object(
                bucket_name=self.bucket_name, object_name=object_name
            )
            return response, response.headers.get("Content-Type", "application/octet-stream")
        except S3Error as e:
            raise RuntimeError(f"Failed to download file: {e}")

    def get_file_url(self, object_name: str, expires: int = 86400) -> str:
        """Get presigned URL for file.

        Args:
            object_name: Object name in storage
            expires: URL expiration time in seconds

        Returns:
            str: Presigned URL
        """
        try:
            return self.client.presigned_get_object(
                bucket_name=self.bucket_name, object_name=object_name, expires=expires
            )
        except S3Error as e:
            raise RuntimeError(f"Failed to get file URL: {e}")

    def delete_file(self, object_name: str) -> None:
        """Delete file from Minio.

        Args:
            object_name: Object name in storage
        """
        try:
            self.client.remove_object(bucket_name=self.bucket_name, object_name=object_name)
        except S3Error as e:
            raise RuntimeError(f"Failed to delete file: {e}")


# Create a default storage instance
storage = MinioStorage()
