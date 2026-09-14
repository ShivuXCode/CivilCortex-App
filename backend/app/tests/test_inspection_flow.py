import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_civilcortex.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_full_inspection_flow():
    # 1. Register/Login to get token
    client.post("/api/register", json={"email": "flow@example.com", "password": "password", "full_name": "Flow"})
    login_resp = client.post("/api/login", data={"username": "flow@example.com", "password": "password"})
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create building to analyze
    # Normally we have an endpoint for this, we will just use building_id=1 and let it fail if it checks it
    # Wait, Step 1 just takes building_id and creates Inspection.
    
    # 2. Step 1 - Analyze Image
    with open(__file__, "rb") as f:
        resp1 = client.post(
            "/api/inspections/analyze",
            headers=headers,
            data={"building_id": 1},
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert "inspection_id" in data1
    assert data1["requires_confirmation"] is True
    
    inspection_id = data1["inspection_id"]
    cv_result = data1["cv_result"]
    
    # 3. Step 2 - Confirm Crack (NEW)
    resp2 = client.post(
        f"/api/inspections/{inspection_id}/confirm-crack",
        headers=headers,
        json={
            "decision": "NEW",
            "observation_data": {
                "image_base64": data1["image_base64"],
                "cv_result": cv_result,
                "severity_level": "high",
                "element_type": "column"
            }
        }
    )
    
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["status"] == "success"
    assert "observation_id" in data2
    assert "risk" in data2
    assert "recommendation" in data2
