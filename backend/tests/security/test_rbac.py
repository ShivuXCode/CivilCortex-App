import pytest

def test_rbac_assessment_patch(client, user_a_headers, engineer_a_headers, admin_a_headers):
    # Setup hierarchy with user_a
    resp = client.post("/api/buildings", json={"name": "Building RBAC"}, headers=user_a_headers)
    b_id = resp.json()["id"]
    
    resp = client.post("/api/inspections/", json={"building_id": b_id}, headers=user_a_headers)
    insp_id = resp.json()["id"]

    # We need a defect and an assessment
    # Instead of full mock, let's just create them through API or test DB fixture
    # Wait, the best way is a fixture for RBAC test data
    pass

@pytest.fixture
def rbac_test_data(db, user_a):
    from app.models.hierarchy import User, Building, Floor, Area, StructuralElement
    from app.models.inspection import Inspection, InspectionImage
    from app.models.defect import Defect, CrackObservation, Assessment
    
    user = db.query(User).filter(User.email == user_a["email"]).first()
    
    building = Building(name="Test RBAC", owner_id=user.id, organization_id=user.organization_id)
    db.add(building)
    db.commit()
    
    inspection = Inspection(building_id=building.id, inspector_id=user.id)
    db.add(inspection)
    db.commit()
    
    image = InspectionImage(inspection_id=inspection.id, object_key="test", original_filename="test", mime_type="image/jpeg")
    db.add(image)
    db.commit()
    
    defect = Defect(defect_type="crack")
    db.add(defect)
    db.commit()
    
    obs = CrackObservation(defect_id=defect.id, inspection_id=inspection.id, image_id=image.id)
    db.add(obs)
    db.commit()
    
    assessment = Assessment(observation_id=obs.id, severity="LOW", risk="LOW")
    db.add(assessment)
    db.commit()
    
    return {"inspection": inspection, "assessment": assessment}

def test_rbac_inspector_cannot_patch(client, user_a_headers, rbac_test_data):
    assessment_id = rbac_test_data["assessment"].id
    resp = client.patch(f"/api/defects/assessments/{assessment_id}", json={"severity": "HIGH"}, headers=user_a_headers)
    assert resp.status_code == 403

def test_rbac_engineer_can_patch(client, engineer_a_headers, rbac_test_data):
    assessment_id = rbac_test_data["assessment"].id
    resp = client.patch(f"/api/defects/assessments/{assessment_id}", json={"severity": "HIGH", "repair_recommendation": "Fix it"}, headers=engineer_a_headers)
    assert resp.status_code == 200
    assert resp.json()["severity"] == "HIGH"
    
def test_rbac_admin_can_patch(client, admin_a_headers, rbac_test_data):
    # Admins inherit permissions
    assessment_id = rbac_test_data["assessment"].id
    resp = client.patch(f"/api/defects/assessments/{assessment_id}", json={"severity": "CRITICAL"}, headers=admin_a_headers)
    assert resp.status_code == 200
