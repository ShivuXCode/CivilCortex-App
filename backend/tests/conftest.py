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

# Use SQLite for tests as permitted in the instructions when Postgres is unavailable for easy setup, 
# provided it uses a clean slate
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
