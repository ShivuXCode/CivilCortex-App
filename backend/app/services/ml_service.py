import os
import cv2
import numpy as np
import torch
from pathlib import Path
from PIL import Image
from skimage.morphology import skeletonize

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
            return None

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
        import albumentations as A
        from albumentations.pytorch import ToTensorV2
        return A.Compose([
            A.Resize(resolution, resolution),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
            ToTensorV2()
        ])

    @staticmethod
    def extract_aruco_scale(image_path: str, known_marker_size_mm: float = 50.0) -> float:
        """Returns mm_per_pixel of the original image if an ArUco marker is found, else None"""
        img = cv2.imread(image_path)
        if img is None: return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        try:
            aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            parameters = cv2.aruco.DetectorParameters()
            detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
            corners, ids, rejected = detector.detectMarkers(gray)
        except AttributeError:
            aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
            parameters = cv2.aruco.DetectorParameters_create()
            corners, ids, rejected = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
            
        if ids is not None and len(corners) > 0:
            c = corners[0][0]
            width_top = np.linalg.norm(c[0] - c[1])
            width_bottom = np.linalg.norm(c[3] - c[2])
            height_left = np.linalg.norm(c[0] - c[3])
            height_right = np.linalg.norm(c[1] - c[2])
            avg_pixel_size = (width_top + width_bottom + height_left + height_right) / 4.0
            return known_marker_size_mm / avg_pixel_size
        return None

    @staticmethod
    def analyze_image(image_path: str) -> dict:
        """
        Analyzes an image using the real PyTorch segmentation model.
        Falls back to demo-mode pipeline inference if the model is unavailable.
        """
        if not os.path.exists(image_path):
            raise ImageProcessingError("Image not found on disk")

        model = MLService.get_model()

        # --- 1. Scale Calibration (ArUco) ---
        original_img = cv2.imread(image_path)
        orig_height, orig_width = original_img.shape[:2]
        
        orig_mm_per_pixel = MLService.extract_aruco_scale(image_path)
        calibration_method = "ArUco Marker (50mm)" if orig_mm_per_pixel else "None (Uncalibrated)"
        
        mask_mm_per_pixel = None
        if orig_mm_per_pixel:
            scale_x = orig_width / 384.0
            scale_y = orig_height / 384.0
            avg_scale = (scale_x + scale_y) / 2.0
            mask_mm_per_pixel = orig_mm_per_pixel * avg_scale

        # --- Graceful fallback when model file is absent ---
        if model is None:
            logger.info("Using DEMO MODE inference because model weights are missing.")
            
            return {
                "defect_type": "crack",
                "confidence": 0.94,
                "mask_coverage": 0.12,
                "component_count": 3,
                "largest_component_area": 4500,
                "length_mm": 124.6 if mask_mm_per_pixel else None,
                "min_width_mm": 0.8 if mask_mm_per_pixel else None,
                "avg_width_mm": 2.1 if mask_mm_per_pixel else None,
                "max_width_mm": 3.7 if mask_mm_per_pixel else None,
                "calibration_method": calibration_method,
                "model_name": "civilcortex_deeplabv3plus (DEMO)",
                "model_version": "v2.0",
                "model_status": "DEMO"
            }

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
            best_binary_mask = None

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
                largest_stat = max([s for i, s in enumerate(stats) if i > 0 and s[cv2.CC_STAT_AREA] >= MIN_AREA_THRESHOLD], key=lambda s: s[cv2.CC_STAT_AREA])
                largest_area = int(largest_stat[cv2.CC_STAT_AREA])
                if largest_area > best_largest_area:
                    best_defect_type = class_name
                    best_confidence = defect_score
                    best_mask_coverage = mask_coverage
                    best_component_count = component_count
                    best_largest_area = largest_area
                    largest_label = [i for i, s in enumerate(stats) if i > 0 and s[cv2.CC_STAT_AREA] == largest_area][0]
                    best_binary_mask = (labels == largest_label).astype(np.uint8)

            length_mm = None
            min_width_mm = None
            avg_width_mm = None
            max_width_mm = None
            
            if best_binary_mask is not None and mask_mm_per_pixel is not None:
                # Geometry Pipeline (Skeletonization & Distance Transform)
                skeleton = skeletonize(best_binary_mask)
                length_mm = round(np.sum(skeleton) * mask_mm_per_pixel, 2)
                
                dist_transform = cv2.distanceTransform(best_binary_mask, cv2.DIST_L2, 5)
                skeleton_widths = dist_transform[skeleton] * 2.0
                
                valid_widths = skeleton_widths[skeleton_widths > 0]
                if len(valid_widths) > 0:
                    min_width_mm = round(np.min(valid_widths) * mask_mm_per_pixel, 2)
                    avg_width_mm = round(np.mean(valid_widths) * mask_mm_per_pixel, 2)
                    max_width_mm = round(np.max(valid_widths) * mask_mm_per_pixel, 2)

            return {
                "defect_type": best_defect_type,
                "confidence": best_confidence,
                "mask_coverage": best_mask_coverage,
                "component_count": best_component_count,
                "largest_component_area": best_largest_area,
                "length_mm": length_mm,
                "min_width_mm": min_width_mm,
                "avg_width_mm": avg_width_mm,
                "max_width_mm": max_width_mm,
                "calibration_method": calibration_method,
                "model_name": "civilcortex_deeplabv3plus",
                "model_version": "v2.0",
                "model_status": "PRODUCTION"
            }
        except Exception as e:
            if isinstance(e, CVInferenceError):
                raise
            logger.error(f"CV Inference failed: {e}")
            raise CVInferenceError(f"CV Inference failed: {e}")
