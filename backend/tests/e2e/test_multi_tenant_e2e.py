"""
E2E Multi-Tenancy / IDOR Tests

Verifies that organization isolation is enforced at the API layer.
Users in Organization A must never be able to access, modify, or analyze
resources belonging to Organization B.

Tests cover: Buildings, Inspections, Images, Analysis Jobs, Assessments.

STEP 9 of the Phase 17 validation plan.
"""

import pytest
from io import BytesIO
from tests.e2e.conftest import (
    register_and_login, create_full_hierarchy,
    upload_test_image, TEST_IMAGE_BYTES
)


def setup_org_user(client, email):
    """Register a user (creates their own org automatically) and return their headers + resource IDs."""
    headers = register_and_login(client, email)
    b_resp = client.post("/api/buildings", json={"name": f"Building-{email[:8]}"}, headers=headers)
    assert b_resp.status_code == 200
    b_id = b_resp.json()["id"]

    insp_resp = client.post("/api/inspections/", json={"building_id": b_id}, headers=headers)
    assert insp_resp.status_code == 200
    insp_id = insp_resp.json()["id"]

    img_id = upload_test_image(client, headers, insp_id)

    return headers, b_id, insp_id, img_id


class TestMultiTenancyE2E:
    """Cross-organization IDOR prevention tests."""

    def test_idor_get_building(self, e2e_client):
        """
        Org B user cannot GET Org A's building.
        """
        headers_a, b_a_id, _, _ = setup_org_user(e2e_client, "idor_a_building@civilcortex-e2e.com")
        headers_b, _, _, _ = setup_org_user(e2e_client, "idor_b_building@civilcortex-e2e.com")

        resp = e2e_client.get(f"/api/buildings/{b_a_id}", headers=headers_b)
        assert resp.status_code in (403, 404), (
            f"Org B should not access Org A's building. Got {resp.status_code}: {resp.text}"
        )

    def test_idor_get_inspection(self, e2e_client):
        """Org B user cannot GET Org A's inspection."""
        headers_a, _, insp_a_id, _ = setup_org_user(e2e_client, "idor_a_insp@civilcortex-e2e.com")
        headers_b, _, _, _ = setup_org_user(e2e_client, "idor_b_insp@civilcortex-e2e.com")

        resp = e2e_client.get(f"/api/inspections/{insp_a_id}", headers=headers_b)
        assert resp.status_code in (403, 404), (
            f"Org B should not access Org A's inspection. Got {resp.status_code}"
        )

    def test_idor_upload_image_to_other_inspection(self, e2e_client):
        """Org B cannot upload an image to Org A's inspection."""
        headers_a, _, insp_a_id, _ = setup_org_user(e2e_client, "idor_a_upload@civilcortex-e2e.com")
        headers_b, _, _, _ = setup_org_user(e2e_client, "idor_b_upload@civilcortex-e2e.com")

        files = {"file": ("attack.jpg", BytesIO(TEST_IMAGE_BYTES), "image/jpeg")}
        resp = e2e_client.post(
            f"/api/inspections/{insp_a_id}/images",
            files=files,
            headers=headers_b
        )
        assert resp.status_code in (403, 404), (
            f"Org B should not upload to Org A's inspection. Got {resp.status_code}"
        )

    def test_idor_analyze_other_image(self, e2e_client):
        """Org B cannot trigger analysis on Org A's image."""
        headers_a, _, insp_a_id, img_a_id = setup_org_user(e2e_client, "idor_a_analyze@civilcortex-e2e.com")
        headers_b, _, _, _ = setup_org_user(e2e_client, "idor_b_analyze@civilcortex-e2e.com")

        resp = e2e_client.post(
            f"/api/inspections/{insp_a_id}/images/{img_a_id}/analyze",
            headers=headers_b
        )
        assert resp.status_code in (403, 404), (
            f"Org B should not trigger analysis on Org A's image. Got {resp.status_code}"
        )

    def test_idor_analysis_job_status(self, e2e_client, e2e_db):
        """Org B cannot view Org A's analysis job status."""
        from app.worker import run_analysis_job
        from app.models.analysis import AnalysisJob

        headers_a, _, insp_a_id, img_a_id = setup_org_user(e2e_client, "idor_a_job@civilcortex-e2e.com")
        headers_b, _, _, _ = setup_org_user(e2e_client, "idor_b_job@civilcortex-e2e.com")

        # Org A triggers analysis
        analyze_resp = e2e_client.post(
            f"/api/inspections/{insp_a_id}/images/{img_a_id}/analyze",
            headers=headers_a
        )
        assert analyze_resp.status_code == 200
        job_id = analyze_resp.json()["job_id"]

        # Org B tries to view the job
        resp = e2e_client.get(f"/api/analysis/jobs/{job_id}", headers=headers_b)
        assert resp.status_code in (403, 404), (
            f"Org B should not access Org A's job. Got {resp.status_code}"
        )

    def test_idor_report_access(self, e2e_client, e2e_db):
        """Org B cannot view Org A's inspection assessment."""
        from app.worker import run_analysis_job

        headers_a, _, insp_a_id, img_a_id = setup_org_user(e2e_client, "idor_a_report@civilcortex-e2e.com")
        headers_b, _, _, _ = setup_org_user(e2e_client, "idor_b_report@civilcortex-e2e.com")

        # Org A completes an analysis
        analyze_resp = e2e_client.post(
            f"/api/inspections/{insp_a_id}/images/{img_a_id}/analyze",
            headers=headers_a
        )
        job_id = analyze_resp.json()["job_id"]
        run_analysis_job(job_id, test_db=e2e_db)

        # Org B attempts to view the assessment
        resp = e2e_client.get(f"/api/inspections/{insp_a_id}/assessment", headers=headers_b)
        assert resp.status_code in (403, 404), (
            f"Org B should not access Org A's assessment. Got {resp.status_code}"
        )

    def test_buildings_list_filtered_by_org(self, e2e_client):
        """
        GET /api/buildings should only return the authenticated user's org buildings.
        Org A user should not see Org B buildings in the list.
        """
        headers_a, b_a_id, _, _ = setup_org_user(e2e_client, "idor_list_a@civilcortex-e2e.com")
        headers_b, b_b_id, _, _ = setup_org_user(e2e_client, "idor_list_b@civilcortex-e2e.com")

        # Org A's building list should not contain Org B's building
        resp = e2e_client.get("/api/buildings", headers=headers_a)
        assert resp.status_code == 200
        building_ids = [b["id"] for b in resp.json()]
        assert b_a_id in building_ids
        assert b_b_id not in building_ids, "Org B's building should not appear in Org A's list"
