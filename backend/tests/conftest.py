import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import shutil

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings
from app.models.hierarchy import User
from app.core.limiter import limiter
from unittest.mock import patch, MagicMock

# Disable rate limiting for tests
limiter.enabled = False

# Use SQLite for tests as permitted in the instructions when Postgres is unavailable for easy setup, 
# provided it uses a clean slate
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def mock_storage():
    with patch('app.services.storage_service.StorageService.upload_file') as mock_upload, \
         patch('app.services.storage_service.StorageService.get_file_bytes') as mock_get_bytes, \
         patch('app.services.storage_service.StorageService.download_file') as mock_download:
        
        mock_upload.return_value = "mock_object_key"
        mock_get_bytes.return_value = b"mock_data"
        
        def mock_download_side_effect(object_key, file_path):
            if object_key.startswith("/tmp/non-existent-file-404"):
                from app.core.exceptions import StorageError
                raise StorageError("missing on disk")
            import cv2
            import numpy as np
            dummy_img = np.zeros((10, 10, 3), dtype=np.uint8)
            cv2.imwrite(file_path, dummy_img)
            
        mock_download.side_effect = mock_download_side_effect
        
        with patch('app.services.rag_service.RagService.retrieve_evidence') as mock_rag:
            mock_rag.return_value = []
            yield mock_upload

@pytest.fixture(scope="session", autouse=True)
def mock_redis_queue():
    with patch('app.worker.analysis_queue') as mock:
        yield mock

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    
    # Cleanup storage
    test_storage = "storage/images/"
    if os.path.exists(test_storage):
        shutil.rmtree(test_storage, ignore_errors=True)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]

@pytest.fixture
def test_user(client):
    user_data = {"email": "test@civilcortex.com", "password": "password123"}
    response = client.post("/api/auth/register", json=user_data)
    if response.status_code == 400: # Already registered
        pass
    return user_data

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/api/auth/login", data={"username": test_user["email"], "password": test_user["password"]})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def user_a(client):
    user_data = {"email": "inspector_a@civilcortex.com", "password": "password123"}
    client.post("/api/auth/register", json=user_data)
    return user_data

@pytest.fixture
def user_a_headers(client, user_a):
    response = client.post("/api/auth/login", data={"username": user_a["email"], "password": user_a["password"]})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def user_b(client):
    user_data = {"email": "inspector_b@civilcortex.com", "password": "password123"}
    client.post("/api/auth/register", json=user_data)
    return user_data

@pytest.fixture
def user_b_headers(client, user_b):
    response = client.post("/api/auth/login", data={"username": user_b["email"], "password": user_b["password"]})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def engineer_a(client, db, user_a):
    # Engineer needs to be in the same org as user_a for some tests
    user_data = {"email": "engineer_a@civilcortex.com", "password": "password123"}
    client.post("/api/auth/register", json=user_data)
    
    # Manually promote to engineer and set organization_id
    from app.models.hierarchy import User
    u_a = db.query(User).filter(User.email == user_a["email"]).first()
    eng = db.query(User).filter(User.email == user_data["email"]).first()
    eng.role = "ENGINEER"
    eng.organization_id = u_a.organization_id
    db.commit()
    
    return user_data

@pytest.fixture
def engineer_a_headers(client, engineer_a):
    response = client.post("/api/auth/login", data={"username": engineer_a["email"], "password": engineer_a["password"]})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_a(client, db, user_a):
    user_data = {"email": "admin_a@civilcortex.com", "password": "password123"}
    client.post("/api/auth/register", json=user_data)
    
    from app.models.hierarchy import User
    u_a = db.query(User).filter(User.email == user_a["email"]).first()
    admin = db.query(User).filter(User.email == user_data["email"]).first()
    admin.role = "ADMIN"
    admin.organization_id = u_a.organization_id
    db.commit()
    
    return user_data

@pytest.fixture
def admin_a_headers(client, admin_a):
    response = client.post("/api/auth/login", data={"username": admin_a["email"], "password": admin_a["password"]})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
