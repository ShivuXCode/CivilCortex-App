import pytest
from pydantic import ValidationError
from metadata_schema import ImageMetadata, DefectInstance, CalibrationData
from annotation_validator import validate_image_metadata
from quality_report_generator import generate_quality_report
from ingestion import calculate_phash
from pathlib import Path
from PIL import Image

def test_near_duplicate_grouping(tmp_path):
    img_path1 = tmp_path / "img1.jpg"
    img1 = Image.new('RGB', (100, 100), color='blue')
    img1.save(img_path1)
    
    # Same image, just saved again (in reality, resize or slight artifact)
    img_path2 = tmp_path / "img2.jpg"
    img2 = img1.resize((50, 50))
    img2.save(img_path2)
    
    phash1 = calculate_phash(img_path1)
    phash2 = calculate_phash(img_path2)
    
    # phash is identical for resized images
    assert phash1 == phash2

def test_provenance_preservation():
    metadata = ImageMetadata(
        image_id="img1",
        source_id="sdnet2018",
        image_width=100,
        image_height=100,
        capture_device="DSLR",
        dataset_version="v0.1",
        preprocessing_history=["resized", "cropped"]
    )
    assert metadata.source_id == "sdnet2018"
    assert metadata.capture_device == "DSLR"
    assert "cropped" in metadata.preprocessing_history

def test_missing_optional_metadata():
    # Should not raise validation error if optional fields are missing
    metadata = ImageMetadata(
        image_id="img1",
        source_id="civilcortex-field",
        image_width=100,
        image_height=100
    )
    assert metadata.site_id is None
    assert metadata.building_id is None
    assert metadata.inspection_id is None

def test_invalid_defect_type():
    defect = DefectInstance(
        defect_instance_id="d1", defect_type="invalid_type", polygon=[[0,0], [10,0], [0,10]], bounding_box=[0,0,10,10]
    )
    img = ImageMetadata(image_id="i1", source_id="s1", image_width=100, image_height=100, defects=[defect])
    errors = validate_image_metadata(img)
    assert any("Invalid defect_type" in e for e in errors)

def test_invalid_morphology():
    defect = DefectInstance(
        defect_instance_id="d1", defect_type="crack", morphology_labels=["invalid_morph"], polygon=[[0,0], [10,0], [0,10]], bounding_box=[0,0,10,10]
    )
    img = ImageMetadata(image_id="i1", source_id="s1", image_width=100, image_height=100, defects=[defect])
    errors = validate_image_metadata(img)
    assert any("Invalid morphology" in e for e in errors)

def test_invalid_polygon():
    # < 3 points
    defect = DefectInstance(
        defect_instance_id="d1", defect_type="crack", polygon=[[0,0], [10,0]], bounding_box=[0,0,10,0]
    )
    img = ImageMetadata(image_id="i1", source_id="s1", image_width=100, image_height=100, defects=[defect])
    errors = validate_image_metadata(img)
    assert any("Polygon too small" in e for e in errors)

def test_thin_crack_annotation_handling():
    # A perfectly valid thin crack polygon (e.g. 2px wide) should pass
    defect = DefectInstance(
        defect_instance_id="d1", defect_type="crack", 
        polygon=[[10,10], [12,10], [12,100], [10,100]], bounding_box=[10,10,12,100]
    )
    img = ImageMetadata(image_id="i1", source_id="s1", image_width=200, image_height=200, defects=[defect])
    errors = validate_image_metadata(img)
    assert len(errors) == 0

def test_calibrated_measurement_validation():
    calib = CalibrationData(is_calibrated=True, reference_object="Ruler", pixels_per_mm=10.5)
    img = ImageMetadata(image_id="i1", source_id="s1", image_width=200, image_height=200, calibration=calib)
    assert img.calibration.is_calibrated is True
    assert img.calibration.pixels_per_mm == 10.5

def test_empty_dataset_reporting(tmp_path):
    report = generate_quality_report(str(tmp_path))
    assert report["total_images"] == 0
    assert report["total_defect_instances"] == 0
    assert report["quality_failures"] == 0

def test_pii_rejection():
    # If PII is found, quality_status should be REJECTED
    metadata = ImageMetadata(
        image_id="img_pii",
        source_id="civilcortex-field",
        image_width=100,
        image_height=100,
        quality_status="REJECTED"
    )
    assert metadata.quality_status == "REJECTED"

def test_uncalibrated_physical_measurement_rejection():
    # It should not claim to have pixels_per_mm if is_calibrated is False
    calib = CalibrationData(is_calibrated=False)
    assert calib.pixels_per_mm is None

def test_dataset_acceptance_gate(tmp_path):
    report = generate_quality_report(str(tmp_path))
    # Test the gate logic against the report
    passed_gate = (
        report["total_images"] > 0 and 
        report.get("unique_sites_count", 0) >= 10 and 
        report["total_defect_instances"] >= 2000
    )
    assert passed_gate is False # Empty dataset fails the gate
