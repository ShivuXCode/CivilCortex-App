import pytest
from unittest.mock import patch, MagicMock
from app.models.analysis import AnalysisJob

def test_async_analysis_queueing(client, auth_headers, db):
    # 1. Create hierarchy and inspection
    resp = client.post("/api/buildings", json={"name": "Test Async Building"}, headers=auth_headers)
    b_id = resp.json()["id"]
    
    resp = client.post("/api/inspections/", json={"building_id": b_id}, headers=auth_headers)
    insp_id = resp.json()["id"]
    
    # 2. Upload image
    import numpy as np
    import cv2
    from io import BytesIO
    dummy_img = np.zeros((384, 384, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', dummy_img)
    files = {"file": ("async_test.jpg", BytesIO(encoded.tobytes()), "image/jpeg")}
    resp = client.post(f"/api/inspections/{insp_id}/images", files=files, headers=auth_headers)
    img_id = resp.json()["id"]

    # 3. Request Analysis (should enqueue and return immediately)
    with patch('app.worker.analysis_queue') as mock_queue:
        resp = client.post(f"/api/inspections/{insp_id}/images/{img_id}/analyze", headers=auth_headers)
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "QUEUED"
        assert "job_id" in data
        
        # Verify enqueue was called
        mock_queue.enqueue.assert_called_once()
        
    job_id = data["job_id"]
    
    # 4. Polling endpoint verification
    resp = client.get(f"/api/analysis/{job_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "QUEUED"
    
    # 5. Idempotency Check
    with patch('app.worker.analysis_queue') as mock_queue_2:
        resp = client.post(f"/api/inspections/{insp_id}/images/{img_id}/analyze", headers=auth_headers)
        assert resp.status_code == 200
        data2 = resp.json()
        assert data2["status"] == "QUEUED"
        assert data2["job_id"] == job_id
        # Should NOT enqueue again
        mock_queue_2.enqueue.assert_not_called()

def test_worker_execution_success(db):
    # Setup test data directly using worker logic
    from app.worker import run_analysis_job
    from app.models.hierarchy import Building, User
    from app.models.inspection import Inspection, InspectionImage
    import uuid
    
    # Needs a real mock of AnalysisService to avoid actual LLM calls
    user = User(email=f"worker_{uuid.uuid4()}@test.com", hashed_password="hash", organization_id=str(uuid.uuid4()))
    db.add(user)
    db.commit()
    
    b = Building(name="Worker Building", owner_id=user.id, organization_id=user.organization_id)
    db.add(b)
    db.commit()
    
    insp = Inspection(building_id=b.id, inspector_id=user.id)
    db.add(insp)
    db.commit()
    
    img = InspectionImage(inspection_id=insp.id, object_key="/fake", original_filename="test", mime_type="image/jpeg", file_size=100)
    db.add(img)
    db.commit()
    
    job = AnalysisJob(image_id=img.id, status="QUEUED")
    db.add(job)
    db.commit()
    
    # Execute worker function directly synchronously for test
    with patch('app.worker.AnalysisService.run_synchronous_analysis') as mock_analysis:
        mock_analysis.return_value = {"status": "success"}
        
        run_analysis_job(str(job.id), test_db=db)
        
        db.refresh(job)
        assert job.status == "COMPLETED"
        assert job.started_at is not None
        assert job.completed_at is not None

def test_worker_execution_failure(db):
    # Setup test data
    from app.worker import run_analysis_job
    from app.models.hierarchy import Building, User
    from app.models.inspection import Inspection, InspectionImage
    import uuid
    
    user = User(email=f"fail_{uuid.uuid4()}@test.com", hashed_password="hash", organization_id=str(uuid.uuid4()))
    db.add(user)
    db.commit()
    
    b = Building(name="Fail Building", owner_id=user.id, organization_id=user.organization_id)
    db.add(b)
    db.commit()
    
    insp = Inspection(building_id=b.id, inspector_id=user.id)
    db.add(insp)
    db.commit()
    
    img = InspectionImage(inspection_id=insp.id, object_key="/fake2", original_filename="test", mime_type="image/jpeg", file_size=100)
    db.add(img)
    db.commit()
    
    job = AnalysisJob(image_id=img.id, status="QUEUED")
    db.add(job)
    db.commit()
    
    with patch('app.worker.AnalysisService.run_synchronous_analysis') as mock_analysis:
        mock_analysis.side_effect = Exception("Simulated Failure")
        
        run_analysis_job(str(job.id), test_db=db)
        
        db.refresh(job)
        assert job.status == "FAILED"
        assert job.error_message == "INTERNAL_ERROR"
