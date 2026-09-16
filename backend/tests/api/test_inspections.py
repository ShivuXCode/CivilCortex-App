import pytest
from io import BytesIO

def test_inspection_creation_and_upload(client, user_a_headers):
    # 1. Create Building
    resp = client.post("/api/buildings", json={"name": "Building B"}, headers=user_a_headers)
    b_id = resp.json()["id"]
    
    # 2. Create Inspection
    resp = client.post("/api/inspections/", json={"building_id": b_id}, headers=user_a_headers)
    assert resp.status_code == 200, resp.json()
    insp_id = resp.json()["id"]
    
    # 3. Upload Image
    import cv2
    import numpy as np
    dummy_img = np.zeros((384, 384, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', dummy_img)
    file_data = encoded.tobytes()
    files = {"file": ("test.jpg", BytesIO(file_data), "image/jpeg")}
    resp = client.post(f"/api/inspections/{insp_id}/images", files=files, headers=user_a_headers)
    assert resp.status_code == 200
    img_id = resp.json()["id"]
    
    # 4. Trigger Analysis
    resp = client.post(f"/api/inspections/{insp_id}/images/{img_id}/analyze", headers=user_a_headers)
    assert resp.status_code == 200
    analysis = resp.json()
    assert analysis["status"] == "QUEUED"

def test_inspection_not_found(client, user_a_headers):
    resp = client.get("/api/inspections/non-existent-uuid", headers=user_a_headers)
    assert resp.status_code == 400 or resp.status_code == 404
