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
        self.use_local_fs = not bool(settings.MINIO_ENDPOINT)
        self.local_dir = settings.STORAGE_ROOT

        if self.use_local_fs:
            os.makedirs(self.local_dir, exist_ok=True)
            self._available = True
            logger.info("StorageService: Using local filesystem mock.")
            return

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
            logger.error(f"StorageService: MinIO initialization failed: {e}")
            raise StorageError(f"MinIO initialization failed: {e}")

    def health_check(self) -> bool:
        """Return True if the storage backend is reachable and the bucket exists."""
        if self.use_local_fs:
            return True
        try:
            return self._available and self.client is not None and self.client.bucket_exists(self.bucket_name)
        except Exception:
            return False

    def upload_file(self, file_obj: BinaryIO, object_key: str, file_size: int, content_type: str = "application/octet-stream") -> str:
        """Uploads a file object to MinIO or Local FS."""
        if self.use_local_fs:
            filepath = os.path.join(self.local_dir, object_key.replace("/", "_"))
            with open(filepath, "wb") as f:
                f.write(file_obj.read())
            return object_key

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
        """Downloads an object from MinIO or Local FS to a local path."""
        if self.use_local_fs:
            filepath = os.path.join(self.local_dir, object_key.replace("/", "_"))
            if not os.path.exists(filepath):
                raise StorageError("File not found locally")
            with open(filepath, "rb") as src, open(destination_path, "wb") as dst:
                dst.write(src.read())
            return

        if not self.client:
            raise StorageError("Storage service is not initialized")
            
        try:
            self.client.fget_object(self.bucket_name, object_key, destination_path)
        except Exception as e:
            logger.error(f"Failed to download from storage: {e}")
            raise StorageError(f"Failed to download from storage: {e}")
            
    def get_file_bytes(self, object_key: str) -> bytes:
        """Gets an object directly as bytes."""
        if self.use_local_fs:
            filepath = os.path.join(self.local_dir, object_key.replace("/", "_"))
            if not os.path.exists(filepath):
                raise StorageError("File not found locally")
            with open(filepath, "rb") as f:
                return f.read()

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
        """Deletes an object from MinIO or Local FS."""
        if self.use_local_fs:
            filepath = os.path.join(self.local_dir, object_key.replace("/", "_"))
            if os.path.exists(filepath):
                os.remove(filepath)
            return

        if not self.client:
            raise StorageError("Storage service is not initialized")
            
        try:
            self.client.remove_object(self.bucket_name, object_key)
        except Exception as e:
            logger.error(f"Failed to delete object: {e}")
            raise StorageError(f"Failed to delete object: {e}")

# Global instance
storage_service = StorageService()
