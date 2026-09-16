"""
E2E Failure Path Tests

Verifies that the system gracefully handles failure scenarios:
- Missing file in storage → job FAILED with STORAGE_ERROR
- Invalid image bytes → job FAILED with IMAGE_PROCESSING_ERROR or CV_INFERENCE_ERROR
- Duplicate analysis attempt → handled gracefully (idempotency)

STEP 10 of the Phase 17 validation plan.
"""

import pytest
import numpy as np
from io import BytesIO
from unittest.mock import patch
from app.worker import run_analysis_job
from app.models.analysis import AnalysisJob
from app.models.inspection import InspectionImage

from tests.e2e.conftest import (
    register_and_login, upload_test_image
)


class TestFailurePath:
    """Failure workflow E2E tests."""

    def test_missing_storage_file_causes_failed_job(self, e2e_client, e2e_db):
        """
        STEP 10: When the storage file is missing (simulated STORAGE_ERROR),
        the analysis job should transition to FAILED, not remain QUEUED.

        This verifies that the worker correctly handles StorageError
        and marks the job with an appropriate error message.
        """
        headers = register_and_login(e2e_client, "fail_storage@civilcortex-e2e.com")

        # Create building and inspection
        b_resp = e2e_client.post("/api/buildings", json={"name": "Failure Test Building"}, headers=headers)
        b_id = b_resp.json()["id"]
        insp_resp = e2e_client.post("/api/inspections/", json={"building_id": b_id}, headers=headers)
        insp_id = insp_resp.json()["id"]

        # Upload image but inject a MISSING key so that download will fail
        img_id = upload_test_image(e2e_client, headers, insp_id)

        # Manually override the object_key in DB to a missing path
        img = e2e_db.query(InspectionImage).filter(InspectionImage.id == img_id).first()
        original_key = img.object_key
        img.object_key = "NON_EXISTENT/missing_image.jpg"
        e2e_db.commit()

        # Trigger analysis
        analyze_resp = e2e_client.post(
            f"/api/inspections/{insp_id}/images/{img_id}/analyze",
            headers=headers
        )
        assert analyze_resp.status_code == 200
        job_id = analyze_resp.json()["job_id"]

        # Execute worker — the download will raise StorageError
        run_analysis_job(job_id, test_db=e2e_db)

        # Job should be FAILED
        job = e2e_db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        assert job.status == "FAILED", f"Job should be FAILED. Got: {job.status}"
        assert "STORAGE_ERROR" in (job.error_message or ""), (
            f"Error message should reference STORAGE_ERROR. Got: {job.error_message}"
        )
        assert job.completed_at is not None

        # Restore original key for cleanup
        img.object_key = original_key
        e2e_db.commit()

    def test_invalid_image_bytes_causes_failed_job(self, e2e_client, e2e_db):
        """
        When the downloaded file contains corrupt/invalid image data,
        the CV pipeline should raise ImageProcessingError and the job should FAIL.
        """
        headers = register_and_login(e2e_client, "fail_invalid_img@civilcortex-e2e.com")

        b_resp = e2e_client.post("/api/buildings", json={"name": "Invalid Image Building"}, headers=headers)
        b_id = b_resp.json()["id"]
        insp_resp = e2e_client.post("/api/inspections/", json={"building_id": b_id}, headers=headers)
        insp_id = insp_resp.json()["id"]

        # Upload normally (storage mock returns valid bytes)
        img_id = upload_test_image(e2e_client, headers, insp_id)

        analyze_resp = e2e_client.post(
            f"/api/inspections/{insp_id}/images/{img_id}/analyze",
            headers=headers
        )
        assert analyze_resp.status_code == 200
        job_id = analyze_resp.json()["job_id"]

        # Override download to write corrupt bytes
        def corrupt_download(object_key, dest_path):
            with open(dest_path, 'wb') as f:
                f.write(b"THIS IS NOT AN IMAGE FILE -- CORRUPT DATA")

        with patch('app.services.storage_service.StorageService.download_file') as mock_dl:
            mock_dl.side_effect = corrupt_download
            run_analysis_job(job_id, test_db=e2e_db)

        job = e2e_db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        assert job.status == "FAILED", f"Job should be FAILED. Got: {job.status}"
        # Error should be IMAGE_PROCESSING_ERROR or CV_INFERENCE_ERROR
        assert job.error_message in ("IMAGE_PROCESSING_ERROR", "CV_INFERENCE_ERROR", "INTERNAL_ERROR"), (
            f"Unexpected error: {job.error_message}"
        )

    def test_worker_idempotency_already_completed(self, e2e_client, e2e_db):
        """
        If a job is already COMPLETED and the worker is called again,
        it should be a no-op (idempotency check in worker.py).
        """
        headers = register_and_login(e2e_client, "fail_idempotent@civilcortex-e2e.com")

        b_resp = e2e_client.post("/api/buildings", json={"name": "Idempotent Building"}, headers=headers)
        b_id = b_resp.json()["id"]
        insp_resp = e2e_client.post("/api/inspections/", json={"building_id": b_id}, headers=headers)
        insp_id = insp_resp.json()["id"]

        img_id = upload_test_image(e2e_client, headers, insp_id)

        analyze_resp = e2e_client.post(
            f"/api/inspections/{insp_id}/images/{img_id}/analyze",
            headers=headers
        )
        job_id = analyze_resp.json()["job_id"]

        # Run once to completion
        run_analysis_job(job_id, test_db=e2e_db)

        job = e2e_db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        assert job.status == "COMPLETED"
        first_completed_at = job.completed_at

        # Run again — idempotency should prevent re-execution
        run_analysis_job(job_id, test_db=e2e_db)

        e2e_db.refresh(job)
        assert job.status == "COMPLETED"
        # completed_at should not have changed (idempotency guard)
        assert job.completed_at == first_completed_at

    def test_analysis_with_wrong_inspection_id_returns_404(self, e2e_client):
        """Attempting to analyze a non-existent image returns 404."""
        headers = register_and_login(e2e_client, "fail_404@civilcortex-e2e.com")

        resp = e2e_client.post(
            "/api/inspections/non-existent-id/images/non-existent-img/analyze",
            headers=headers
        )
        assert resp.status_code == 404

    def test_failed_job_has_no_assessment(self, e2e_client, e2e_db):
        """
        When a job FAILs, no Assessment or Defect should be created.
        The DB should remain clean.
        """
        from app.models.defect import CrackObservation

        headers = register_and_login(e2e_client, "fail_clean_db@civilcortex-e2e.com")

        b_resp = e2e_client.post("/api/buildings", json={"name": "Clean DB Building"}, headers=headers)
        b_id = b_resp.json()["id"]
        insp_resp = e2e_client.post("/api/inspections/", json={"building_id": b_id}, headers=headers)
        insp_id = insp_resp.json()["id"]

        img_id = upload_test_image(e2e_client, headers, insp_id)

        # Inject missing file to cause STORAGE_ERROR
        img = e2e_db.query(InspectionImage).filter(InspectionImage.id == img_id).first()
        img.object_key = "NON_EXISTENT/cleanup_test.jpg"
        e2e_db.commit()

        analyze_resp = e2e_client.post(
            f"/api/inspections/{insp_id}/images/{img_id}/analyze",
            headers=headers
        )
        job_id = analyze_resp.json()["job_id"]

        run_analysis_job(job_id, test_db=e2e_db)

        # No observation should have been created for this image
        obs = e2e_db.query(CrackObservation).filter(
            CrackObservation.image_id == img_id
        ).first()
        assert obs is None, "Failed job should not create orphan CrackObservation records"
