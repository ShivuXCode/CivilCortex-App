import pytest

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

    # Assert get building details
    resp = client.get(f"/api/buildings/{b_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["floors"]) == 1

def test_create_building_invalid(client, auth_headers):
    resp = client.post("/api/buildings", json={}, headers=auth_headers)
    assert resp.status_code == 422
