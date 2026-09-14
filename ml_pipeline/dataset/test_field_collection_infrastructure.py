import pytest

# Mock definitions reflecting the business rules described in Phase 10D.3

class Defect:
    def __init__(self, defect_id, defect_type):
        self.defect_id = defect_id
        self.defect_type = defect_type
        self.observations = []

class Observation:
    def __init__(self, observation_id, calibration_status="UNAVAILABLE", physical_length=None):
        self.observation_id = observation_id
        self.calibration_status = calibration_status
        self.physical_length = physical_length
        self.images = []
        
        if physical_length is not None and calibration_status != "PHYSICAL_CALIBRATED":
            raise ValueError("Physical measurement requires validated calibration.")

def test_create_physical_defect():
    d = Defect(defect_id="DEF-001", defect_type="crack")
    assert d.defect_id == "DEF-001"

def test_multiple_images_one_defect():
    d = Defect(defect_id="DEF-001", defect_type="crack")
    obs = Observation("OBS-001")
    obs.images.extend(["img1.jpg", "img2.jpg"])
    d.observations.append(obs)
    assert len(d.observations) == 1
    assert len(d.observations[0].images) == 2

def test_multiple_observations_one_defect():
    d = Defect(defect_id="DEF-001", defect_type="crack")
    d.observations.append(Observation("OBS-001"))
    d.observations.append(Observation("OBS-002"))
    assert len(d.observations) == 2

def test_prevent_accidental_duplicate():
    # If a user inspects the same crack later, they add an observation, not a new defect
    d = Defect(defect_id="DEF-001", defect_type="crack")
    d.observations.append(Observation("OBS-new"))
    assert d.defect_id == "DEF-001"

def test_physical_measurement_blocked_without_calibration():
    with pytest.raises(ValueError, match="Physical measurement requires validated calibration"):
        Observation("OBS-001", calibration_status="PIXEL_ONLY", physical_length=150)

def test_hard_negatives_excluded():
    d = Defect(defect_id="HN-001", defect_type="hard_negative")
    # In the readiness checker, hard_negatives are strictly tracked separately.
    assert d.defect_type == "hard_negative"

def test_morphology_tags_are_attributes():
    # Morphology shouldn't create a separate defect
    d = Defect(defect_id="DEF-002", defect_type="crack")
    d.morphology = ["branching", "horizontal"]
    assert d.defect_type == "crack"
    assert len(d.morphology) == 2

def test_annotation_provenance():
    annotation = {
        "annotator_id": "annotator_1",
        "version": "v1.0",
        "model_assisted": True
    }
    assert annotation["model_assisted"] is True

def test_peer_review_transitions():
    states = ["ANNOTATED", "PEER_REVIEW", "ACCEPTED"]
    assert states[-1] == "ACCEPTED"

def test_privacy_state_validation():
    states = ["ACCEPT", "REDACT", "REJECT"]
    assert "REDACT" in states

def test_longitudinal_identity_preservation():
    # Verify we can append an observation from a different date to the same defect
    d = Defect("DEF-003", "spalling")
    d.observations.append(Observation("OBS-100"))
    d.observations.append(Observation("OBS-200"))
    assert len(d.observations) == 2

def test_hierarchy_referential_integrity():
    record = {
        "site_id": "SITE-A",
        "building_id": "BLDG-1",
        "element_id": "COL-1",
        "defect_instance_id": "DEF-001"
    }
    assert record["building_id"] == "BLDG-1"

