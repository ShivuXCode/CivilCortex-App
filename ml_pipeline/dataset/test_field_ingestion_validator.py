import pytest
from field_ingestion_validator import FieldIngestionValidator

@pytest.fixture
def base_record():
    return {
        "source_id": "SRC_1",
        "site_id": "SITE_1",
        "building_id": "BLD_1",
        "floor_id": "FLR_1",
        "area_id": "AREA_1",
        "structural_element_id": "ELE_1",
        "inspection_id": "INSP_1",
        "observation_id": "OBS_1",
        "image_id": "IMG_1",
        "schema_version": "v0.1",
        "dataset_version": "v0.1",
        "annotation_version": "v0.1",
        "privacy_status": "ACCEPT",
        "calibration_status": "PIXEL_ONLY",
        "checksum": "abc123hash",
        "defect_instances": [
            {
                "defect_instance_id": "DEF_1",
                "defect_type": "crack",
                "morphology_labels": ["branching", "vertical"]
            }
        ]
    }

def test_valid_record(base_record):
    validator = FieldIngestionValidator()
    status, errors = validator.validate_record(base_record)
    assert status == "VALID"
    assert len(errors) == 0

def test_missing_hierarchy(base_record):
    validator = FieldIngestionValidator()
    del base_record["floor_id"]
    status, errors = validator.validate_record(base_record)
    assert status == "INVALID"
    assert any("Missing required hierarchy field: floor_id" in e for e in errors)

def test_invalid_taxonomy(base_record):
    validator = FieldIngestionValidator()
    base_record["defect_instances"][0]["defect_type"] = "rust"
    status, errors = validator.validate_record(base_record)
    assert status == "INVALID"
    assert any("Invalid defect type: rust" in e for e in errors)

def test_invalid_calibration(base_record):
    validator = FieldIngestionValidator()
    base_record["calibration_status"] = "PIXEL_ONLY"
    base_record["physical_measurements"] = {"width_mm": 5.0}
    status, errors = validator.validate_record(base_record)
    assert status == "INVALID"
    assert any("Physical measurements present but calibration status is PIXEL_ONLY" in e for e in errors)

def test_cross_record_consistency(base_record):
    validator = FieldIngestionValidator()
    validator.validate_record(base_record)
    
    # Second record changes the structural element for the same defect
    record2 = base_record.copy()
    record2["image_id"] = "IMG_2"
    record2["checksum"] = "def456hash"
    record2["structural_element_id"] = "ELE_2"
    
    status, errors = validator.validate_record(record2)
    assert status == "INVALID"
    assert any("Hierarchy mismatch: defect DEF_1 assigned to multiple structural elements" in e for e in errors)

def test_duplicate_image(base_record):
    validator = FieldIngestionValidator()
    validator.validate_record(base_record)
    status, errors = validator.validate_record(base_record)
    assert status == "INVALID"
    assert any("Duplicate image checksum found" in e for e in errors)

def test_invalid_morphology(base_record):
    validator = FieldIngestionValidator()
    base_record["defect_instances"][0]["morphology_labels"] = ["wiggly"]
    status, errors = validator.validate_record(base_record)
    assert status == "INVALID"
    assert any("Invalid morphology tag: wiggly" in e for e in errors)

