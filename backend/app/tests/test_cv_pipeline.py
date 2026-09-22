import pytest
import os
from datetime import datetime, timezone
from app.schemas.api_models import CVAnalysisResult, CVDetection, CVGeometry, CVMeasurement, ImageQualityResult
from app.services.cv_pipeline import ImageQualityGate
from app.models.domain_models import ImageQualityRejectionReason, ImageStatus, DefectType, CrackMorphology, CalibrationStatus

def test_taxonomy_validation():
    # DefectType and CrackMorphology should allow valid instantiation
    dt = DefectType.CRACK.value
    assert dt == "crack"
    cm = CrackMorphology.DIAGONAL.value
    assert cm == "diagonal"

def test_multiple_detections_and_morphology():
    det1 = CVDetection(
        detection_id="d1",
        defect_type=DefectType.CRACK.value,
        morphology_tags=[CrackMorphology.DIAGONAL.value, CrackMorphology.BRANCHING.value],
        model_confidence=0.88,
        bounding_box=[10, 10, 50, 50]
    )
    det2 = CVDetection(
        detection_id="d2",
        defect_type=DefectType.SPALLING.value,
        morphology_tags=[],
        model_confidence=0.75,
        bounding_box=[100, 100, 150, 150]
    )
    res = CVAnalysisResult(
        image_id="img1",
        image_width=800,
        image_height=600,
        inference_timestamp=datetime.now(timezone.utc),
        quality=ImageQualityResult(quality_score=1.0, is_pass=True),
        detections=[det1, det2]
    )
    assert len(res.detections) == 2
    assert CrackMorphology.DIAGONAL.value in res.detections[0].morphology_tags
    assert CrackMorphology.BRANCHING.value in res.detections[0].morphology_tags

def generate_test_image(width, height, color):
    import cv2
    import numpy as np
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = color
    _, encoded = cv2.imencode('.jpg', img)
    return encoded.tobytes()

def test_image_quality_pass():
    # 800x600 image, well lit (gray 128) -> wait, uniform image has 0 blur variance (laplacian = 0)
    # Let's add noise to pass blur check
    import cv2
    import numpy as np
    img = np.random.randint(50, 200, (600, 800, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', img)
    quality = ImageQualityGate.evaluate(encoded.tobytes())
    assert quality.is_pass is True

def test_image_quality_rejection_resolution():
    import cv2
    import numpy as np
    img = np.random.randint(50, 200, (400, 400, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', img)
    quality = ImageQualityGate.evaluate(encoded.tobytes())
    assert quality.is_pass is False
    assert ImageQualityRejectionReason.MIN_RESOLUTION.value in quality.rejection_reasons

def test_image_quality_rejection_exposure():
    import cv2
    import numpy as np
    # Dark image
    img = np.random.randint(0, 15, (600, 800, 3), dtype=np.uint8)
    _, encoded = cv2.imencode('.jpg', img)
    quality = ImageQualityGate.evaluate(encoded.tobytes())
    assert quality.is_pass is False
    assert ImageQualityRejectionReason.UNDEREXPOSED.value in quality.rejection_reasons

def test_corrupted_image_handling():
    quality = ImageQualityGate.evaluate(b"not an image")
    assert quality.is_pass is False
    assert ImageQualityRejectionReason.FILE_CORRUPTION.value in quality.rejection_reasons

def test_calibration_state_validation():
    # Valid pixel only
    meas = CVMeasurement(
        pixel_length=100.0,
        calibration_status=CalibrationStatus.PIXEL_ONLY.value
    )
    assert meas.physical_length is None

    # Invalid: physical length with PIXEL_ONLY
    with pytest.raises(ValueError, match="Cannot contain physical dimensions"):
        CVMeasurement(
            pixel_length=100.0,
            physical_length=50.0,
            calibration_status=CalibrationStatus.PIXEL_ONLY.value
        )
    
    # Invalid: PHYSICAL_CALIBRATED without reference
    with pytest.raises(ValueError, match="PHYSICAL_CALIBRATED requires a calibration_reference"):
        CVMeasurement(
            physical_length=50.0,
            calibration_status=CalibrationStatus.PHYSICAL_CALIBRATED.value
        )


def test_cv_engineering_boundary():
    # The CV result should not have ANY fields relating to "shear failure", "safety", "repair"
    det = CVDetection(
        detection_id="d1",
        defect_type=DefectType.CRACK.value,
        model_confidence=0.9,
        bounding_box=[0, 0, 10, 10]
    )
    assert not hasattr(det, "shear_failure")
    assert not hasattr(det, "safety_status")
    assert not hasattr(det, "repair_method")
