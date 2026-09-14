import pytest
from io import BytesIO

def test_registration_and_login(client):
    # Test registration
    resp = client.post("/api/auth/register", json={"email": "newuser@test.com", "password": "pass"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "newuser@test.com"
    
    # Test duplicate registration
    resp = client.post("/api/auth/register", json={"email": "newuser@test.com", "password": "pass"})
    assert resp.status_code == 400
    
    # Test login
    resp = client.post("/api/auth/login", data={"username": "newuser@test.com", "password": "pass"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_building_hierarchy(client, auth_headers):
    # 1. Create Building
    resp = client.post("/api/buildings", json={"name": "Building A"}, headers=auth_headers)
    assert resp.status_code == 200
    b_id = resp.json()["id"]
    
    # 2. Create Floor
    resp = client.post("/api/floors", json={"name": "Floor 1", "building_id": b_id}, headers=auth_headers)
    assert resp.status_code == 200
    f_id = resp.json()["id"]
    
    # 3. Create Area
    resp = client.post("/api/areas", json={"name": "Living Room", "floor_id": f_id}, headers=auth_headers)
    assert resp.status_code == 200
    a_id = resp.json()["id"]
    
    # 4. Create Structural Element
    resp = client.post("/api/structural-elements", json={"name": "Beam A", "element_type": "BEAM", "area_id": a_id}, headers=auth_headers)
    assert resp.status_code == 200
    se_id = resp.json()["id"]
    
    # Assert get buildings works
    resp = client.get("/api/buildings", headers=auth_headers)
    assert len(resp.json()) >= 1

    return b_id, se_id

def test_inspection_and_defects(client, auth_headers):
    # First create a hierarchy
    b_id, se_id = test_building_hierarchy(client, auth_headers)
    
    # 1. Create Inspection
    resp = client.post("/api/inspections/", json={"building_id": b_id}, headers=auth_headers)
    assert resp.status_code == 200
    insp_id = resp.json()["id"]
    
    # 2. Upload Image
    file_data = b"fake image data"
    files = {"file": ("test.jpg", BytesIO(file_data), "image/jpeg")}
    resp = client.post(f"/api/inspections/{insp_id}/images", files=files, headers=auth_headers)
    assert resp.status_code == 200
    img_id = resp.json()["id"]
    
    # 3. Analyze Image (ML Service)
    resp = client.post(f"/api/inspections/{insp_id}/images/{img_id}/analyze", headers=auth_headers)
    assert resp.status_code == 200
    analysis = resp.json()
    assert analysis["model_status"] == "DEVELOPMENT"
    
    # 4. Create Defect
    resp = client.post("/api/defects/", json={"structural_element_id": se_id, "defect_type": analysis["defect_type"]}, headers=auth_headers)
    assert resp.status_code == 200
    defect_id = resp.json()["id"]
    assert resp.json()["status"] == "CANDIDATE"
    
    # 5. Create Observation
    obs_data = {"defect_id": defect_id, "inspection_id": insp_id, "image_id": img_id}
    resp = client.post("/api/defects/observations", json=obs_data, headers=auth_headers)
    assert resp.status_code == 200
    obs_id = resp.json()["id"]
    
    # 6. Create Assessment
    assess_data = {"severity": "LOW", "risk": "REQUIRES_REVIEW"}
    resp = client.post(f"/api/defects/observations/{obs_id}/assessments", json=assess_data, headers=auth_headers)
    assert resp.status_code == 200
    
    # 7. Update Defect State Transition
    # valid transition
    resp = client.put(f"/api/defects/{defect_id}", json={"status": "MONITORED"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "MONITORED"
    
    # invalid transition
    resp = client.put(f"/api/defects/{defect_id}", json={"status": "DISMISSED"}, headers=auth_headers)
    assert resp.status_code == 400

def test_access_control(client, auth_headers):
    # User 1 creates building
    b_id, se_id = test_building_hierarchy(client, auth_headers)
    
    # User 2 logs in
    client.post("/api/auth/register", json={"email": "hacker@test.com", "password": "pass"})
    resp = client.post("/api/auth/login", data={"username": "hacker@test.com", "password": "pass"})
    hacker_headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    
    # User 2 tries to create an inspection on User 1's building
    resp = client.post("/api/inspections/", json={"building_id": b_id}, headers=hacker_headers)
    assert resp.status_code == 403
