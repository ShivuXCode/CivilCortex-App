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
