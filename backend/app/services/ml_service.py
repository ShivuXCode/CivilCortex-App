import os
import cv2
import numpy as np
import tensorflow as tf
from pathlib import Path
from app.core.exceptions import ImageProcessingError, CVInferenceError
from app.core.logger import logger

class MLService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            try:
                def dummy_loss(y_true, y_pred): return y_pred
                def dummy_metric(y_true, y_pred): return y_pred
                
                model_path = os.path.join(os.path.dirname(__file__), "../models/civilcortex_best.keras")
                cls._model = tf.keras.models.load_model(model_path, custom_objects={
                    'combined_loss': dummy_loss,
                    'dice_metric': dummy_metric,
                    'iou_metric': dummy_metric
                }, compile=False)
            except Exception as e:
                logger.error(f"Failed to load ML model: {e}")
                raise CVInferenceError(f"Failed to load ML model: {e}")
        return cls._model

    @staticmethod
    def analyze_image(image_path: str) -> dict:
        """
        Analyzes an image using the real Keras segmentation model.
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError("Image not found on disk")
            
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ImageProcessingError("Invalid image or unsupported format")
                
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img, (384, 384))
            
            # Normalize to [0, 1]
            img_normalized = img_resized.astype(np.float32) / 255.0
            
            input_tensor = np.expand_dims(img_normalized, axis=0) # (1, 384, 384, 3)
        except Exception as e:
            if isinstance(e, ImageProcessingError):
                raise
            logger.error(f"Failed to process image {image_path}: {e}")
            raise ImageProcessingError(f"Failed to process image: {e}")
        
        try:
            model = MLService.get_model()
            mask = model.predict(input_tensor, verbose=0)
            
            # 1. Binarize Mask (Probability threshold)
            prob_threshold = 0.5
            binary_mask = (mask[0, :, :, 0] > prob_threshold).astype(np.uint8)
            
            # 2. Extract Connected Components
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)
            
            # 3. Compute Spatial Metrics
            total_pixels = binary_mask.size
            mask_coverage = float(np.sum(binary_mask) / total_pixels)
            
            # Filter components (ignore background component 0)
            MIN_AREA_THRESHOLD = 50
            valid_components = [s[cv2.CC_STAT_AREA] for i, s in enumerate(stats) if i > 0 and s[cv2.CC_STAT_AREA] >= MIN_AREA_THRESHOLD]
            
            component_count = len(valid_components)
            largest_component_area = int(max(valid_components)) if component_count > 0 else 0
            
            # 4. Defect Decision
            defect_score = float(largest_component_area / total_pixels) if component_count > 0 else 0.0
            defect_type = "crack" if component_count > 0 else "none"
            
            return {
                "defect_type": defect_type,
                "confidence": defect_score,  # Defect score based on largest contiguous area ratio
                "mask_coverage": mask_coverage,
                "component_count": component_count,
                "largest_component_area": largest_component_area,
                "model_name": "civilcortex_segmentation",
                "model_version": "v1.0",
                "model_status": "PRODUCTION"
            }
        except Exception as e:
            if isinstance(e, CVInferenceError):
                raise
            logger.error(f"CV Inference failed: {e}")
            raise CVInferenceError(f"CV Inference failed: {e}")

