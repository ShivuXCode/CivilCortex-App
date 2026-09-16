import pytest

@pytest.fixture
def org_b_data(db, user_b):
    # Setup some data in Org B
    from app.models.hierarchy import User, Building
    from app.models.inspection import Inspection, InspectionImage
    
    user = db.query(User).filter(User.email == user_b["email"]).first()
    
    building = Building(name="Org B Building", owner_id=user.id, organization_id=user.organization_id)
    db.add(building)
    db.commit()
    
    inspection = Inspection(building_id=building.id, inspector_id=user.id)
    db.add(inspection)
    db.commit()
    
    image = InspectionImage(inspection_id=inspection.id, object_key="test", original_filename="test", mime_type="image/jpeg")
    db.add(image)
    db.commit()
    
    return {"building": building, "inspection": inspection, "image": image}

def test_idor_get_building(client, user_a_headers, org_b_data):
    # User A tries to GET User B's building
    resp = client.get(f"/api/buildings/{org_b_data['building'].id}", headers=user_a_headers)
    assert resp.status_code == 404

def test_idor_create_inspection_on_other_building(client, user_a_headers, org_b_data):
    # User A tries to create an inspection on User B's building
    resp = client.post("/api/inspections/", json={"building_id": org_b_data['building'].id}, headers=user_a_headers)
    assert resp.status_code == 403

def test_idor_get_inspection(client, user_a_headers, org_b_data):
    # User A tries to GET User B's inspection
    resp = client.get(f"/api/inspections/{org_b_data['inspection'].id}/report", headers=user_a_headers)
    assert resp.status_code == 403 or resp.status_code == 404

def test_idor_upload_image_to_other_inspection(client, user_a_headers, org_b_data):
    import cv2
    import numpy as np
    from io import BytesIO
    dummy_img = np.zeros((10, 10, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', dummy_img)
    files = {"file": ("test.jpg", BytesIO(encoded.tobytes()), "image/jpeg")}
    
    resp = client.post(f"/api/inspections/{org_b_data['inspection'].id}/images", files=files, headers=user_a_headers)
    assert resp.status_code == 403 or resp.status_code == 404

def test_idor_analyze_other_image(client, user_a_headers, org_b_data):
    resp = client.post(f"/api/inspections/{org_b_data['inspection'].id}/images/{org_b_data['image'].id}/analyze", headers=user_a_headers)
    assert resp.status_code == 403 or resp.status_code == 404
