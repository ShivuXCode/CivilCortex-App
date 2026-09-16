"""
E2E test conftest.py

Environment boundaries (documented):
- PostgreSQL: UNAVAILABLE → SQLite used
- Redis/RQ: UNAVAILABLE → run_analysis_job() called in-process
- MinIO: UNAVAILABLE → storage mocked (upload returns key, download writes real image)
- Gemini: UNAVAILABLE → LangGraph runs but agent6 returns graceful error string (not exception)
- TensorFlow/Keras: AVAILABLE → REAL CV inference (not mocked)
- ChromaDB: AVAILABLE but EMPTY → RAG returns []
"""

import pytest
import os
import shutil
import cv2
import numpy as np
import tempfile
from io import BytesIO
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.limiter import limiter

# Disable rate limiting for tests
limiter.enabled = False

# E2E uses a dedicated, isolated SQLite database
E2E_DATABASE_URL = "sqlite:///./e2e_test.db"

engine = create_engine(
    E2E_DATABASE_URL, connect_args={"check_same_thread": False}
)
E2ESessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_real_test_image() -> bytes:
    """Creates a realistic 384x384 test image that the real CV model can process."""
    img = np.zeros((384, 384, 3), dtype=np.uint8)
    # Add a simulated crack-like line to give the model something to detect
    cv2.line(img, (50, 50), (300, 320), (180, 180, 180), 2)
    cv2.line(img, (80, 60), (290, 330), (160, 160, 160), 1)
    # Add some texture
    noise = np.random.randint(0, 30, (384, 384, 3), dtype=np.uint8)
    img = cv2.add(img, noise)
    _, encoded = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return encoded.tobytes()


# Create the real test image bytes once
TEST_IMAGE_BYTES = create_real_test_image()


@pytest.fixture(scope="session", autouse=True)
def e2e_mock_storage():
    """
    Mock MinIO storage for E2E.

    Upload: returns a deterministic object key.
    Download: writes the real test image to the destination path so that
              the REAL ML model can process it (CV is NOT mocked).
    """
    with patch('app.services.storage_service.StorageService.upload_file') as mock_upload, \
         patch('app.services.storage_service.StorageService.download_file') as mock_download, \
         patch('app.services.storage_service.StorageService.get_file_bytes') as mock_get_bytes:

        mock_upload.return_value = "e2e/test_inspection_image.jpg"
        mock_get_bytes.return_value = TEST_IMAGE_BYTES

        def download_side_effect(object_key, dest_path):
            # If key is a simulated missing file, raise StorageError
            if "MISSING" in object_key or "NON_EXISTENT" in object_key:
                from app.core.exceptions import StorageError
                raise StorageError("Object not found in storage")
            # Otherwise write the real test image — real CV will process it
            with open(dest_path, 'wb') as f:
                f.write(TEST_IMAGE_BYTES)

        mock_download.side_effect = download_side_effect

        with patch('app.services.rag_service.RagService.retrieve_evidence') as mock_rag:
            mock_rag.return_value = []  # ChromaDB is empty — documented limitation
            yield mock_upload


@pytest.fixture(scope="session", autouse=True)
def e2e_mock_redis():
    """Mock Redis queue — Redis is unavailable. Worker is run in-process."""
    with patch('app.worker.analysis_queue') as mock_queue:
        yield mock_queue


@pytest.fixture(scope="session", autouse=True)
def e2e_setup_db():
    """Create and tear down the E2E database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./e2e_test.db"):
        os.remove("./e2e_test.db")


@pytest.fixture
def e2e_db():
    """Per-test DB session."""
    db = E2ESessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def e2e_client(e2e_db):
    """FastAPI test client wired to the E2E database."""
    def override_get_db():
        try:
            yield e2e_db
        finally:
            e2e_db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


# ─── User / Auth helpers ────────────────────────────────────────────────────

def register_and_login(client, email, password="E2ePassw0rd!"):
    """Register (if not exists) and return auth headers."""
    client.post("/api/auth/register", json={"email": email, "password": password})
    resp = client.post("/api/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, f"Login failed for {email}: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_user_id(client, headers):
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    return resp.json()["id"], resp.json().get("organization_id")


def promote_user(db, email, role):
    """Directly promote a user to engineer/admin in the DB."""
    from app.models.hierarchy import User
    user = db.query(User).filter(User.email == email).first()
    assert user is not None, f"User {email} not found"
    user.role = role.upper()
    db.commit()
    db.refresh(user)
    return user


def set_same_org(db, email_a, email_b):
    """Set user B to be in the same org as user A."""
    from app.models.hierarchy import User
    u_a = db.query(User).filter(User.email == email_a).first()
    u_b = db.query(User).filter(User.email == email_b).first()
    assert u_a and u_b
    u_b.organization_id = u_a.organization_id
    db.commit()


# ─── Hierarchy helpers ───────────────────────────────────────────────────────

def create_full_hierarchy(client, headers, prefix="E2E"):
    """Create Building → Floor → Area → StructuralElement and return all IDs."""
    b = client.post("/api/buildings", json={"name": f"{prefix} Building"}, headers=headers)
    assert b.status_code == 200, b.text
    b_id = b.json()["id"]

    f = client.post("/api/floors", json={"name": f"{prefix} Floor 1", "floor_number": 1, "building_id": b_id}, headers=headers)
    assert f.status_code == 200, f.text
    f_id = f.json()["id"]

    a = client.post("/api/areas", json={"name": f"{prefix} Area A", "floor_id": f_id}, headers=headers)
    assert a.status_code == 200, a.text
    a_id = a.json()["id"]

    e = client.post("/api/structural-elements",
                    json={"name": f"{prefix} Column 1", "element_type": "COLUMN", "area_id": a_id}, headers=headers)
    assert e.status_code == 200, e.text
    e_id = e.json()["id"]

    return b_id, f_id, a_id, e_id


def upload_test_image(client, headers, insp_id):
    """Upload the real test image and return image_id."""
    files = {"file": ("test_crack.jpg", BytesIO(TEST_IMAGE_BYTES), "image/jpeg")}
    resp = client.post(f"/api/inspections/{insp_id}/images", files=files, headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()["id"]
