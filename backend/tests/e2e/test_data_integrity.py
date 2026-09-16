"""
E2E Database Integrity Tests

After a complete golden-path analysis, verify that all database relationships
are correct and no orphan/duplicate records exist.

Checks:
- User → Organization relationship
- Building → Organization relationship
- Inspection → Building, Inspector
- InspectionImage → Inspection, object_key populated
- AnalysisJob → InspectionImage
- CrackObservation → Defect, Inspection, Image
- Assessment → CrackObservation
- No duplicate Defects for one image
- No duplicate Assessments for one Observation
- Failed job has no persisted Assessment

STEP 11 of the Phase 17 validation plan.
"""

import pytest
from app.worker import run_analysis_job
from app.models.analysis import AnalysisJob
from app.models.hierarchy import User, Building
from app.models.inspection import Inspection, InspectionImage
from app.models.defect import Defect, CrackObservation, Assessment

from tests.e2e.conftest import (
    register_and_login, create_full_hierarchy, upload_test_image
)


class TestDatabaseIntegrity:
    """Database relationship and integrity verification after analysis."""

    def test_user_org_assignment(self, e2e_client, e2e_db):
        """Every registered user should be assigned to an organization."""
        headers = register_and_login(e2e_client, "integrity_org@civilcortex-e2e.com")
        me_resp = e2e_client.get("/api/auth/me", headers=headers)
        user_data = me_resp.json()

        user = e2e_db.query(User).filter(User.id == user_data["id"]).first()
        assert user is not None
        assert user.organization_id is not None, "User must be assigned to an organization on registration"

    def test_building_org_isolation(self, e2e_client, e2e_db):
        """Buildings created by a user are assigned to that user's organization."""
        headers = register_and_login(e2e_client, "integrity_building@civilcortex-e2e.com")
        me_resp = e2e_client.get("/api/auth/me", headers=headers)
        user_org_id = me_resp.json()["organization_id"]

        b_resp = e2e_client.post("/api/buildings", json={"name": "Integrity Building"}, headers=headers)
        b_id = b_resp.json()["id"]

        building = e2e_db.query(Building).filter(Building.id == b_id).first()
        assert building.organization_id == user_org_id

    def test_full_relationship_chain_after_analysis(self, e2e_client, e2e_db):
        """
        After a complete analysis:
        User → Org → Building → Inspection → Image → AnalysisJob → Defect → Observation → Assessment

        All relationships must be non-null and consistent.
        """
        headers = register_and_login(e2e_client, "integrity_chain@civilcortex-e2e.com")
        me_resp = e2e_client.get("/api/auth/me", headers=headers)
        user_id = me_resp.json()["id"]
        user_org_id = me_resp.json()["organization_id"]

        # Build hierarchy
        b_id, _, _, _ = create_full_hierarchy(e2e_client, headers, "INTEGRITY")

        # Create inspection
        insp_resp = e2e_client.post("/api/inspections/", json={"building_id": b_id}, headers=headers)
        insp_id = insp_resp.json()["id"]

        # Upload image
        img_id = upload_test_image(e2e_client, headers, insp_id)

        # Trigger and run analysis
        analyze_resp = e2e_client.post(
            f"/api/inspections/{insp_id}/images/{img_id}/analyze",
            headers=headers
        )
        job_id = analyze_resp.json()["job_id"]
        run_analysis_job(job_id, test_db=e2e_db)

        # ── Verify chain ──────────────────────────────────────────────────

        # Inspection
        inspection = e2e_db.query(Inspection).filter(Inspection.id == insp_id).first()
        assert inspection is not None
        assert inspection.building_id == b_id
        assert inspection.inspector_id == user_id

        # Building org
        building = e2e_db.query(Building).filter(Building.id == b_id).first()
        assert building.organization_id == user_org_id

        # InspectionImage
        img = e2e_db.query(InspectionImage).filter(InspectionImage.id == img_id).first()
        assert img.inspection_id == insp_id
        assert img.object_key is not None and img.object_key != ""

        # AnalysisJob
        job = e2e_db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        assert job.image_id == img_id
        assert job.status == "COMPLETED"

        # CrackObservation
        observation = e2e_db.query(CrackObservation).filter(
            CrackObservation.image_id == img_id
        ).first()
        assert observation is not None
        assert observation.inspection_id == insp_id

        # Defect
        defect = e2e_db.query(Defect).filter(Defect.id == observation.defect_id).first()
        assert defect is not None
        assert defect.defect_type is not None

        # Assessment
        assessment = e2e_db.query(Assessment).filter(
            Assessment.observation_id == observation.id
        ).first()
        assert assessment is not None
        assert assessment.severity is not None
        assert assessment.risk is not None

    def test_no_duplicate_defects_per_image(self, e2e_client, e2e_db):
        """
        One image analysis should produce exactly one Defect.
        Running the worker once must not create duplicate Defect records.
        """
        headers = register_and_login(e2e_client, "integrity_nodup@civilcortex-e2e.com")

        b_resp = e2e_client.post("/api/buildings", json={"name": "No Dup Building"}, headers=headers)
        b_id = b_resp.json()["id"]
        insp_resp = e2e_client.post("/api/inspections/", json={"building_id": b_id}, headers=headers)
        insp_id = insp_resp.json()["id"]

        img_id = upload_test_image(e2e_client, headers, insp_id)

        analyze_resp = e2e_client.post(
            f"/api/inspections/{insp_id}/images/{img_id}/analyze",
            headers=headers
        )
        job_id = analyze_resp.json()["job_id"]
        run_analysis_job(job_id, test_db=e2e_db)

        # Count Observations for this image
        observations = e2e_db.query(CrackObservation).filter(
            CrackObservation.image_id == img_id
        ).all()
        assert len(observations) == 1, (
            f"Expected exactly 1 observation per image. Found {len(observations)}"
        )

        # Count Assessments for this observation
        assessments = e2e_db.query(Assessment).filter(
            Assessment.observation_id == observations[0].id
        ).all()
        assert len(assessments) == 1, (
            f"Expected exactly 1 assessment per observation. Found {len(assessments)}"
        )

    def test_no_orphan_observations_after_failed_job(self, e2e_client, e2e_db):
        """
        A failed job should not leave orphan CrackObservation records.
        """
        headers = register_and_login(e2e_client, "integrity_orphan@civilcortex-e2e.com")

        b_resp = e2e_client.post("/api/buildings", json={"name": "Orphan Check Building"}, headers=headers)
        b_id = b_resp.json()["id"]
        insp_resp = e2e_client.post("/api/inspections/", json={"building_id": b_id}, headers=headers)
        insp_id = insp_resp.json()["id"]

        img_id = upload_test_image(e2e_client, headers, insp_id)

        # Force storage failure
        img = e2e_db.query(InspectionImage).filter(InspectionImage.id == img_id).first()
        img.object_key = "NON_EXISTENT/orphan_test.jpg"
        e2e_db.commit()

        analyze_resp = e2e_client.post(
            f"/api/inspections/{insp_id}/images/{img_id}/analyze",
            headers=headers
        )
        job_id = analyze_resp.json()["job_id"]
        run_analysis_job(job_id, test_db=e2e_db)

        # No orphan observations
        orphan_obs = e2e_db.query(CrackObservation).filter(
            CrackObservation.image_id == img_id
        ).all()
        assert len(orphan_obs) == 0, (
            f"Failed job should not create orphan observations. Found: {len(orphan_obs)}"
        )

    def test_image_object_key_stored(self, e2e_client, e2e_db):
        """
        Uploaded images must store the object_key in the DB (not empty/null).
        This verifies that Phase 9 (File Storage) is working.
        """
        headers = register_and_login(e2e_client, "integrity_key@civilcortex-e2e.com")

        b_resp = e2e_client.post("/api/buildings", json={"name": "Key Test Building"}, headers=headers)
        b_id = b_resp.json()["id"]
        insp_resp = e2e_client.post("/api/inspections/", json={"building_id": b_id}, headers=headers)
        insp_id = insp_resp.json()["id"]

        img_id = upload_test_image(e2e_client, headers, insp_id)

        img = e2e_db.query(InspectionImage).filter(InspectionImage.id == img_id).first()
        assert img.object_key is not None
        assert img.object_key != ""
        assert img.file_size > 0
        assert img.mime_type is not None
