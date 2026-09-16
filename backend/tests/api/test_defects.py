import pytest

def test_defects_and_assessments(client, user_a_headers):
    # 1. Create Building & Element
    resp = client.post("/api/buildings", json={"name": "Building C"}, headers=user_a_headers)
    b_id = resp.json()["id"]
    
    resp = client.post("/api/floors", json={"name": "F1", "building_id": b_id}, headers=user_a_headers)
    f_id = resp.json()["id"]
    
    resp = client.post("/api/areas", json={"name": "A1", "floor_id": f_id}, headers=user_a_headers)
    a_id = resp.json()["id"]
    
    resp = client.post("/api/structural-elements", json={"name": "S1", "element_type": "BEAM", "area_id": a_id}, headers=user_a_headers)
    se_id = resp.json()["id"]

    # 2. Create Defect
    resp = client.post("/api/defects/", json={"structural_element_id": se_id, "defect_type": "spalling"}, headers=user_a_headers)
    assert resp.status_code == 200
    defect_id = resp.json()["id"]
    
    # 3. Update Defect State Transition
    resp = client.put(f"/api/defects/{defect_id}", json={"status": "MONITORED"}, headers=user_a_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "MONITORED"
    
    # invalid transition
    resp = client.put(f"/api/defects/{defect_id}", json={"status": "DISMISSED"}, headers=user_a_headers)
    assert resp.status_code == 400
