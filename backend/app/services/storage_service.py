import os
import io
import mimetypes
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from app.core.exceptions import StorageError
from app.core.logger import logger
from typing import BinaryIO, Optional
import urllib3

class StorageService:
    def __init__(self):
        self.client = None
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._available = False

        try:
            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ROOT_USER,
                secret_key=settings.MINIO_ROOT_PASSWORD,
                secure=settings.MINIO_SECURE,
                http_client=urllib3.PoolManager(
                    retries=urllib3.Retry(total=3, backoff_factor=0.2)
                )
            )
            # Try to make the bucket if it doesn't exist
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
            self._available = True
            logger.info("StorageService: MinIO connection established successfully.")
        except Exception as e:
            # Re-raise as a domain error so it surfaces at startup or first use.
            # Previously this was swallowed (logger.warning only), making root-cause
            # diagnosis very difficult in production.
            logger.error(f"StorageService: MinIO initialization failed: {e}")
            raise StorageError(f"MinIO initialization failed: {e}")

    def health_check(self) -> bool:
        """Return True if the storage backend is reachable and the bucket exists."""
        try:
            return self._available and self.client is not None and self.client.bucket_exists(self.bucket_name)
        except Exception:
            return False

    def upload_file(self, file_obj: BinaryIO, object_key: str, file_size: int, content_type: str = "application/octet-stream") -> str:
        """Uploads a file object to MinIO."""
        if not self.client:
            raise StorageError("Storage service is not initialized")
            
        try:
            self.client.put_object(
                self.bucket_name,
                object_key,
                file_obj,
                length=file_size,
                content_type=content_type
            )
            return object_key
        except Exception as e:
            logger.error(f"Failed to upload to storage: {e}")
            raise StorageError(f"Failed to upload to storage: {e}")
            
    def download_file(self, object_key: str, destination_path: str):
        """Downloads an object from MinIO to a local path."""
        if not self.client:
            raise StorageError("Storage service is not initialized")
            
        try:
            self.client.fget_object(self.bucket_name, object_key, destination_path)
        except Exception as e:
            logger.error(f"Failed to download from storage: {e}")
            raise StorageError(f"Failed to download from storage: {e}")
            
    def get_file_bytes(self, object_key: str) -> bytes:
        """Gets an object directly as bytes."""
        if not self.client:
            raise StorageError("Storage service is not initialized")
            
        try:
            response = self.client.get_object(self.bucket_name, object_key)
            return response.read()
        except Exception as e:
            logger.error(f"Failed to get object from storage: {e}")
            raise StorageError(f"Failed to get object from storage: {e}")
        finally:
            if 'response' in locals() and hasattr(response, 'close'):
                response.close()
                
    def delete_file(self, object_key: str):
        """Deletes an object from MinIO."""
        if not self.client:
            raise StorageError("Storage service is not initialized")
            
        try:
            self.client.remove_object(self.bucket_name, object_key)
        except Exception as e:
            logger.error(f"Failed to delete object: {e}")
            raise StorageError(f"Failed to delete object: {e}")

# Global instance
storage_service = StorageService()
