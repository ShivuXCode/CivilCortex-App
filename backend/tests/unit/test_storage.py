import pytest
import tempfile
import os
from io import BytesIO
from app.services.storage_service import storage_service
from minio.error import S3Error

@pytest.fixture(autouse=True)
def setup_minio():
    """Ensure the test bucket exists and clean it up."""
    if not storage_service.client:
        pytest.skip("MinIO is not available in this environment")
        
    bucket = storage_service.bucket_name
    try:
        if not storage_service.client.bucket_exists(bucket):
            storage_service.client.make_bucket(bucket)
    except Exception:
        pytest.skip("MinIO connection failed")
        
    yield
    
    # Cleanup bucket contents (optional, but good practice)
    # We could iterate and delete objects, but we'll leave it for now
    # or just delete the specific test keys in the tests.

def test_upload_and_download_file():
    test_content = b"fake image content"
    test_key = "tests/fake_image.jpg"
    
    # Upload
    file_obj = BytesIO(test_content)
    storage_service.upload_file(file_obj, test_key, len(test_content), "image/jpeg")
    
    # Download
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        temp_path = tmp.name
        
    try:
        storage_service.download_file(test_key, temp_path)
        with open(temp_path, "rb") as f:
            downloaded_content = f.read()
        assert downloaded_content == test_content
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    # Cleanup
    storage_service.delete_file(test_key)

def test_get_file_bytes():
    test_content = b"more fake content"
    test_key = "tests/fake_bytes.jpg"
    
    # Upload
    file_obj = BytesIO(test_content)
    storage_service.upload_file(file_obj, test_key, len(test_content), "image/jpeg")
    
    # Get bytes
    downloaded_content = storage_service.get_file_bytes(test_key)
    assert downloaded_content == test_content
    
    # Cleanup
    storage_service.delete_file(test_key)

def test_download_nonexistent_file():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        temp_path = tmp.name
        
    try:
        from app.core.exceptions import StorageError
        with pytest.raises(StorageError) as exc_info:
            storage_service.download_file("nonexistent/file.jpg", temp_path)
        assert "Failed to download from storage" in str(exc_info.value)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
