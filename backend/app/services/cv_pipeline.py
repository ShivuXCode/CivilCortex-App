import cv2
import numpy as np
import uuid
from datetime import datetime, timezone
from app.schemas.api_models import (
    CVAnalysisResult, CVDetection, CVGeometry, CVMeasurement, ImageQualityResult
)
from app.models.domain_models import ImageQualityRejectionReason, ImageStatus, DefectType, CrackMorphology, CalibrationStatus, MeasurementMethod

class ImageQualityGate:
    MIN_WIDTH = 480
    MIN_HEIGHT = 480
    MIN_BLUR_VARIANCE = 100.0  # Threshold for Laplacian variance (sharpness)
    MIN_EXPOSURE = 20.0        # Avoid extremely dark images
    MAX_EXPOSURE = 235.0       # Avoid overexposed images

    @classmethod
    def evaluate(cls, image_bytes: bytes) -> ImageQualityResult:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        reasons = []
        is_pass = True
        quality_score = 1.0

        if img is None:
            return ImageQualityResult(
                quality_score=0.0,
                is_pass=False,
                rejection_reasons=[ImageQualityRejectionReason.FILE_CORRUPTION.value]
            )
        
        h, w = img.shape[:2]
        if w < cls.MIN_WIDTH or h < cls.MIN_HEIGHT:
            is_pass = False
            reasons.append(ImageQualityRejectionReason.MIN_RESOLUTION.value)
            quality_score -= 0.3
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Blur check
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance < cls.MIN_BLUR_VARIANCE:
            is_pass = False
            reasons.append(ImageQualityRejectionReason.BLUR_VARIANCE_TOO_LOW.value)
            quality_score -= 0.4
            
        # Exposure check
        mean_val = np.mean(gray)
        if mean_val < cls.MIN_EXPOSURE:
            is_pass = False
            reasons.append(ImageQualityRejectionReason.UNDEREXPOSED.value)
            quality_score -= 0.3
        elif mean_val > cls.MAX_EXPOSURE:
            is_pass = False
            reasons.append(ImageQualityRejectionReason.OVEREXPOSED.value)
            quality_score -= 0.3

        return ImageQualityResult(
            quality_score=max(0.0, quality_score),
            is_pass=is_pass,
            rejection_reasons=reasons
        )

def run_demo_inference(image_bytes: bytes, image_id: str = None) -> CVAnalysisResult:
    """
    Isolated PIPELINE_DEMO_ONLY adapter.
    """
    quality = ImageQualityGate.evaluate(image_bytes)
    
    # Extract dimensions safely even if corrupt, fallback to 0
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    h, w = img.shape[:2] if img is not None else (0, 0)

    detections = []
    image_status = ImageStatus.NO_DEFECT.value

    # If it passes quality, inject a deterministic demo detection
    if quality.is_pass:
        image_status = ImageStatus.DEFECT_PRESENT.value
        demo_detection = CVDetection(
            detection_id=str(uuid.uuid4()),
            defect_type=DefectType.CRACK.value,
            morphology_tags=[CrackMorphology.DIAGONAL.value, CrackMorphology.BRANCHING.value],
            model_confidence=0.92, # Raw uncalibrated demo confidence
            bounding_box=[0.1, 0.2, 0.5, 0.8], # Normalized [x_min, y_min, x_max, y_max]
            segmentation_mask_ref="s3://mock/masks/demo_mask.json",
            geometry=CVGeometry(orientation_degrees=45.0),
            measurement=CVMeasurement(
                pixel_length=150.5,
                pixel_width=12.2,
                measurement_unit="px",
                measurement_method=MeasurementMethod.MEDIAL_AXIS_EXTRACTION.value,
                calibration_status=CalibrationStatus.PIXEL_ONLY.value
            )
        )
        detections.append(demo_detection)

    return CVAnalysisResult(
        image_id=image_id,
        model_version="PIPELINE_DEMO_ONLY",
        inference_timestamp=datetime.now(timezone.utc),
        image_width=w,
        image_height=h,
        coordinate_convention="normalized_top_left_origin",
        quality=quality,
        image_status=image_status,
        detections=detections
    )
