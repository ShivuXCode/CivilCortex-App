"""
E2E RBAC Test

Verifies Role-Based Access Control across all three roles:
- INSPECTOR: can create inspections, upload, trigger analysis — cannot modify assessments
- ENGINEER: can view and patch assessments
- ADMIN: can view and patch assessments

Frontend note: RBAC UI controls are frontend-only (UX). These tests exercise the BACKEND enforcement.
"""

import pytest
from app.models.analysis import AnalysisJob
from app.worker import run_analysis_job

from tests.e2e.conftest import (
    register_and_login, get_user_id, promote_user, set_same_org,
    create_full_hierarchy, upload_test_image
)


def setup_completed_analysis(client, db, user_email, prefix):
    """
    Helper: Creates a complete hierarchy, inspection, image, and runs the
    analysis pipeline to completion. Returns (insp_id, assessment_id, headers).
    """
    headers = register_and_login(client, user_email)

    b_id, _, _, _ = create_full_hierarchy(client, headers, prefix)
    insp_resp = client.post("/api/inspections/", json={"building_id": b_id}, headers=headers)
    insp_id = insp_resp.json()["id"]

    img_id = upload_test_image(client, headers, insp_id)

    analyze_resp = client.post(
        f"/api/inspections/{insp_id}/images/{img_id}/analyze",
        headers=headers
    )
    assert analyze_resp.status_code == 200
    job_id = analyze_resp.json()["job_id"]

    # Run worker in-process
    run_analysis_job(job_id, test_db=db)

    # Get the assessment ID from the assessment endpoint (Gemini report may be null)
    report_resp = client.get(f"/api/inspections/{insp_id}/assessment", headers=headers)
    assert report_resp.status_code == 200, report_resp.text
    assessment_id = report_resp.json()[0]["id"]

    return insp_id, assessment_id, headers


class TestRBACE2E:
    """Role-Based Access Control end-to-end tests."""

    def test_inspector_cannot_patch_assessment(self, e2e_client, e2e_db):
        """
        STEP 8: Inspectors cannot modify assessment fields.
        Backend must return 403, not just hide the UI.
        """
        insp_id, assessment_id, inspector_headers = setup_completed_analysis(
            e2e_client, e2e_db, "rbac_inspector@civilcortex-e2e.com", "RBAC_INS"
        )

        # Inspector attempts to PATCH the assessment
        patch_resp = e2e_client.patch(
            f"/api/defects/assessments/{assessment_id}",
            json={"repair_recommendation": "Unauthorized repair plan"},
            headers=inspector_headers
        )
        # Backend must enforce 403
        assert patch_resp.status_code == 403, (
            f"Inspector should get 403. Got: {patch_resp.status_code} — {patch_resp.text}"
        )

    def test_engineer_can_patch_assessment(self, e2e_client, e2e_db):
        """
        STEP 7: Engineers can view and modify assessments.
        """
        # Inspector creates the inspection
        insp_id, assessment_id, inspector_headers = setup_completed_analysis(
            e2e_client, e2e_db, "rbac_eng_owner@civilcortex-e2e.com", "RBAC_ENG"
        )

        # Register engineer in same org
        eng_email = "rbac_engineer@civilcortex-e2e.com"
        engineer_headers = register_and_login(e2e_client, eng_email)
        promote_user(e2e_db, eng_email, "ENGINEER")
        set_same_org(e2e_db, "rbac_eng_owner@civilcortex-e2e.com", eng_email)

        # Re-login after promotion
        engineer_headers = register_and_login(e2e_client, eng_email)

        # Engineer can view the assessment
        report_resp = e2e_client.get(
            f"/api/inspections/{insp_id}/assessment",
            headers=engineer_headers
        )
        assert report_resp.status_code == 200

        # Engineer can PATCH the assessment
        patch_resp = e2e_client.patch(
            f"/api/defects/assessments/{assessment_id}",
            json={"repair_recommendation": "Epoxy injection required"},
            headers=engineer_headers
        )
        assert patch_resp.status_code == 200, (
            f"Engineer should be able to patch. Got: {patch_resp.status_code} — {patch_resp.text}"
        )
        assert patch_resp.json()["repair_recommendation"] == "Epoxy injection required"

    def test_admin_can_patch_assessment(self, e2e_client, e2e_db):
        """ADMIN role can also modify assessments."""
        insp_id, assessment_id, inspector_headers = setup_completed_analysis(
            e2e_client, e2e_db, "rbac_admin_owner@civilcortex-e2e.com", "RBAC_ADMIN"
        )

        admin_email = "rbac_admin@civilcortex-e2e.com"
        admin_headers = register_and_login(e2e_client, admin_email)
        promote_user(e2e_db, admin_email, "ADMIN")
        set_same_org(e2e_db, "rbac_admin_owner@civilcortex-e2e.com", admin_email)
        admin_headers = register_and_login(e2e_client, admin_email)

        patch_resp = e2e_client.patch(
            f"/api/defects/assessments/{assessment_id}",
            json={"repair_recommendation": "Admin intervention repair"},
            headers=admin_headers
        )
        assert patch_resp.status_code == 200

    def test_inspector_cannot_access_other_orgs_inspection(self, e2e_client, e2e_db):
        """
        Inspectors from different organizations cannot see each other's inspections.
        """
        # Inspector A creates inspection
        headers_a = register_and_login(e2e_client, "rbac_org_a@civilcortex-e2e.com")
        b_a = e2e_client.post("/api/buildings", json={"name": "Org A Building"}, headers=headers_a)
        b_a_id = b_a.json()["id"]
        insp_a = e2e_client.post("/api/inspections/", json={"building_id": b_a_id}, headers=headers_a)
        insp_a_id = insp_a.json()["id"]

        # Inspector B (separate org — different registration = different org)
        headers_b = register_and_login(e2e_client, "rbac_org_b@civilcortex-e2e.com")

        # Inspector B tries to view Inspector A's inspection
        resp = e2e_client.get(f"/api/inspections/{insp_a_id}", headers=headers_b)
        assert resp.status_code in (403, 404), (
            f"Cross-org access should be denied. Got: {resp.status_code}"
        )

    def test_engineer_review_persists_in_db(self, e2e_client, e2e_db):
        """
        STEP 7: After engineer patches assessment, verify the DB record is updated.
        """
        from app.models.defect import Assessment

        insp_id, assessment_id, _ = setup_completed_analysis(
            e2e_client, e2e_db, "rbac_persist_owner@civilcortex-e2e.com", "RBAC_PERSIST"
        )

        eng_email = "rbac_persist_eng@civilcortex-e2e.com"
        engineer_headers = register_and_login(e2e_client, eng_email)
        promote_user(e2e_db, eng_email, "ENGINEER")
        set_same_org(e2e_db, "rbac_persist_owner@civilcortex-e2e.com", eng_email)
        engineer_headers = register_and_login(e2e_client, eng_email)

        patch_resp = e2e_client.patch(
            f"/api/defects/assessments/{assessment_id}",
            json={"repair_recommendation": "Apply polymer cement mortar patch"},
            headers=engineer_headers
        )
        assert patch_resp.status_code == 200

        # Verify DB
        db_assessment = e2e_db.query(Assessment).filter(Assessment.id == assessment_id).first()
        assert db_assessment.repair_recommendation == "Apply polymer cement mortar patch"
