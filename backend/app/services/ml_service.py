import os
import cv2
import numpy as np
import tensorflow as tf
from pathlib import Path
from app.core.exceptions import ImageProcessingError, CVInferenceError
from app.core.logger import logger

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/civilcortex_best.keras")

class MLService:
    _model = None
    _model_load_attempted = False  # Avoid repeated load attempts on every request

    @classmethod
    def get_model(cls):
        """Load and cache the Keras model. Returns None if the model file is missing."""
        if cls._model_load_attempted:
            return cls._model
        cls._model_load_attempted = True

        if not os.path.exists(_MODEL_PATH):
            logger.warning(
                f"ML model file not found at '{_MODEL_PATH}'. "
                "Analysis will fall back to demo/pipeline mode. "
                "Place 'civilcortex_best.keras' in backend/models/ to enable real inference."
            )
            return None

        try:
            def dummy_loss(y_true, y_pred): return y_pred
            def dummy_metric(y_true, y_pred): return y_pred

            cls._model = tf.keras.models.load_model(_MODEL_PATH, custom_objects={
                'combined_loss': dummy_loss,
                'dice_metric': dummy_metric,
                'iou_metric': dummy_metric
            }, compile=False)
            logger.info("ML model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            raise CVInferenceError(f"Failed to load ML model: {e}")
        return cls._model

    @staticmethod
    def analyze_image(image_path: str) -> dict:
        """
        Analyzes an image using the real Keras segmentation model.
        Falls back to demo-mode pipeline inference if the model is unavailable.
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError("Image not found on disk")

        model = MLService.get_model()

        # --- Graceful fallback when model file is absent ---
        if model is None:
            logger.warning("Using demo-mode CV inference (real model unavailable).")
            from app.services.cv_pipeline import run_demo_inference
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            demo_result = run_demo_inference(image_bytes, image_id=image_path)
            has_defect = len(demo_result.detections) > 0
            return {
                "defect_type": "crack" if has_defect else "none",
                "confidence": demo_result.detections[0].model_confidence if has_defect else 0.0,
                "mask_coverage": None,
                "component_count": len(demo_result.detections),
                "largest_component_area": None,
                "model_name": "DEMO_FALLBACK",
                "model_version": demo_result.model_version,
                "model_status": "DEMO"
            }

        # --- Real model inference ---
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
                "confidence": defect_score,
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
