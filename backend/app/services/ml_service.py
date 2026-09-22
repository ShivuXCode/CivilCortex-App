import os
import cv2
import numpy as np
import torch
from pathlib import Path
from PIL import Image

import segmentation_models_pytorch as smp
import albumentations as A
from albumentations.pytorch import ToTensorV2

from app.core.exceptions import ImageProcessingError, CVInferenceError
from app.core.logger import logger

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../models/Phase6_ArchDeepLabEff_best.pth")

class MLService:
    _model = None
    _model_load_attempted = False
    _device = "cuda" if torch.cuda.is_available() else "cpu"

    @classmethod
    def get_model(cls):
        """Load and cache the PyTorch model. Returns None if the model file is missing."""
        if cls._model_load_attempted:
            return cls._model
        cls._model_load_attempted = True

        if not os.path.exists(_MODEL_PATH):
            logger.warning(
                f"ML model file not found at '{_MODEL_PATH}'. "
                "Place 'Phase6_ArchDeepLabEff_best.pth' in backend/models/ to enable real inference."
            )
            raise CVInferenceError(f"ML model file not found at '{_MODEL_PATH}'")

        try:
            cls._model = smp.DeepLabV3Plus(
                encoder_name="efficientnet-b4",
                encoder_weights=None,
                in_channels=3,
                classes=4
            )
            cls._model.load_state_dict(torch.load(_MODEL_PATH, map_location=cls._device, weights_only=True))
            cls._model.to(cls._device)
            cls._model.eval()
            logger.info(f"PyTorch ML model loaded successfully on {cls._device}.")
        except Exception as e:
            logger.error(f"Failed to load PyTorch ML model: {e}")
            raise CVInferenceError(f"Failed to load ML model: {e}")
        return cls._model

    @staticmethod
    def get_preprocessing(resolution=384):
        return A.Compose([
            A.Resize(resolution, resolution),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2()
        ])

    @staticmethod
    def analyze_image(image_path: str) -> dict:
        """
        Analyzes an image using the real PyTorch segmentation model.
        Falls back to demo-mode pipeline inference if the model is unavailable.
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError("Image not found on disk")

        model = MLService.get_model()

        # --- Graceful fallback when model file is absent ---
        # --- Real model inference ---
        try:
            image = np.array(Image.open(image_path).convert("RGB"))
            preprocess = MLService.get_preprocessing(resolution=384)
            tensor = preprocess(image=image)['image'].unsqueeze(0).to(MLService._device)
        except Exception as e:
            if isinstance(e, ImageProcessingError):
                raise
            logger.error(f"Failed to process image {image_path}: {e}")
            raise ImageProcessingError(f"Failed to process image: {e}")

        try:
            with torch.no_grad():
                logits = model(tensor)
                # Argmax for prediction classes
                prediction = torch.argmax(logits, dim=1).squeeze(0).cpu().numpy()

            # Class mapping: 0=bg, 1=crack, 2=spalling, 3=corrosion
            DEFECT_CLASSES = {1: "crack", 2: "spalling", 3: "corrosion"}

            total_pixels = prediction.size
            best_defect_type = "none"
            best_confidence = 0.0
            best_mask_coverage = 0.0
            best_component_count = 0
            best_largest_area = 0

            # Analyze each defect class independently
            for class_idx, class_name in DEFECT_CLASSES.items():
                binary_mask = (prediction == class_idx).astype(np.uint8)
                
                if np.sum(binary_mask) == 0:
                    continue

                num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)
                
                # Ignore background component
                MIN_AREA_THRESHOLD = 50
                valid_components = [s[cv2.CC_STAT_AREA] for i, s in enumerate(stats) if i > 0 and s[cv2.CC_STAT_AREA] >= MIN_AREA_THRESHOLD]
                
                if not valid_components:
                    continue
                    
                component_count = len(valid_components)
                largest_area = int(max(valid_components))
                mask_coverage = float(np.sum(binary_mask) / total_pixels)
                
                # Confidence score based on largest area ratio (as in the original code)
                defect_score = float(largest_area / total_pixels)
                
                # Select the dominant defect type (largest area)
                if largest_area > best_largest_area:
                    best_defect_type = class_name
                    best_confidence = defect_score
                    best_mask_coverage = mask_coverage
                    best_component_count = component_count
                    best_largest_area = largest_area

            return {
                "defect_type": best_defect_type,
                "confidence": best_confidence,
                "mask_coverage": best_mask_coverage,
                "component_count": best_component_count,
                "largest_component_area": best_largest_area,
                "model_name": "civilcortex_deeplabv3plus",
                "model_version": "v2.0",
                "model_status": "PRODUCTION"
            }
        except Exception as e:
            if isinstance(e, CVInferenceError):
                raise
            logger.error(f"CV Inference failed: {e}")
            raise CVInferenceError(f"CV Inference failed: {e}")
