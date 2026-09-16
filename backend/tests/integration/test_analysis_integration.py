import pytest
import os
import tempfile
import cv2
import numpy as np
from io import BytesIO
import uuid

def create_hierarchy(client, auth_headers):
    # 1. Create Building
    resp = client.post("/api/buildings", json={"name": "Integration Building"}, headers=auth_headers)
    b_id = resp.json()["id"]
    return b_id

def test_analyze_image_success(client, auth_headers, db):
    b_id = create_hierarchy(client, auth_headers)
    
    # Create Inspection
    resp = client.post("/api/inspections/", json={"building_id": b_id}, headers=auth_headers)
    insp_id = resp.json()["id"]
    
    # Upload Image
    dummy_img = np.zeros((384, 384, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', dummy_img)
    file_data = encoded.tobytes()
    files = {"file": ("integration_test.jpg", BytesIO(file_data), "image/jpeg")}
    resp = client.post(f"/api/inspections/{insp_id}/images", files=files, headers=auth_headers)
    img_id = resp.json()["id"]
    
    # Analyze Image (Async trigger)
    from unittest.mock import patch
    with patch('app.worker.analysis_queue') as mock_queue:
        resp = client.post(f"/api/inspections/{insp_id}/images/{img_id}/analyze", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "QUEUED"
        assert "job_id" in data
        job_id = data["job_id"]
        mock_queue.enqueue.assert_called_once()
        
    # Execute worker manually to verify persistence
    from app.worker import run_analysis_job
    with patch('app.worker.AnalysisService.run_synchronous_analysis') as mock_sync:
        mock_sync.return_value = None # Mock success, but doesn't return anything needed by worker
        # Let's let the worker run the REAL AnalysisService to verify DB persistence!
        pass 
        
    # Actually, we WANT to run the real AnalysisService to test integration!
    run_analysis_job(job_id, test_db=db)
    
    # Verify Persistence
    from app.models.defect import Defect, Assessment, CrackObservation
    from app.models.analysis import AnalysisJob
    
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    assert job is not None
    assert job.status == "COMPLETED"
    
    observation = db.query(CrackObservation).filter(CrackObservation.image_id == img_id).first()
    assert observation is not None
    
    defect = db.query(Defect).filter(Defect.id == observation.defect_id).first()
    assert defect is not None
    assert defect.structural_element_id is None # We made this nullable
    
    assessment = db.query(Assessment).filter(Assessment.observation_id == observation.id).first()
    assert assessment is not None

def test_analyze_image_missing_image(client, auth_headers):
    b_id = create_hierarchy(client, auth_headers)
    
    resp = client.post("/api/inspections/", json={"building_id": b_id}, headers=auth_headers)
    insp_id = resp.json()["id"]
    
    # Try to analyze a non-existent image
    resp = client.post(f"/api/inspections/{insp_id}/images/non-existent/analyze", headers=auth_headers)
    assert resp.status_code == 404

def test_analyze_image_missing_inspection(client, auth_headers):
    resp = client.post(f"/api/inspections/non-existent/images/non-existent/analyze", headers=auth_headers)
    assert resp.status_code == 404



def test_analyze_unauthorized_access(client, auth_headers, db):
    # Create with user 1
    b_id = create_hierarchy(client, auth_headers)
    resp = client.post("/api/inspections/", json={"building_id": b_id}, headers=auth_headers)
    insp_id = resp.json()["id"]
    
    import numpy as np
    import cv2
    from io import BytesIO
    dummy_img = np.zeros((384, 384, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', dummy_img)
    files = {"file": ("unauth_test.jpg", BytesIO(encoded.tobytes()), "image/jpeg")}
    
    from unittest.mock import patch
    with patch('app.services.storage_service.StorageService.upload_file') as mock_upload:
        mock_upload.return_value = "mock_key"
        resp = client.post(f"/api/inspections/{insp_id}/images", files=files, headers=auth_headers)
    
    assert resp.status_code == 200, resp.json()
    img_id = resp.json()["id"]
    
    # User 2 logs in
    client.post("/api/auth/register", json={"email": "hacker2@test.com", "password": "password123"})
    resp2 = client.post("/api/auth/login", data={"username": "hacker2@test.com", "password": "password123"})
    hacker_headers = {"Authorization": f"Bearer {resp2.json()['access_token']}"}
    
    # Try to analyze User 1's image
    from unittest.mock import patch
    with patch('app.worker.analysis_queue') as mock_queue:
        resp = client.post(f"/api/inspections/{insp_id}/images/{img_id}/analyze", headers=hacker_headers)
        assert resp.status_code == 403
