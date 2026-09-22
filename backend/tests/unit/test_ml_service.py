import pytest
import os
import cv2
import numpy as np
from app.services.ml_service import MLService
from app.core.exceptions import ImageProcessingError

@pytest.fixture
def valid_image(tmp_path):
    path = tmp_path / "valid.jpg"
    img = np.zeros((480, 480, 3), dtype=np.uint8)
    cv2.imwrite(str(path), img)
    return str(path)

@pytest.fixture
def corrupted_image(tmp_path):
    path = tmp_path / "corrupted.jpg"
    path.write_bytes(b"not an image at all")
    return str(path)

@pytest.fixture
def unsupported_image(tmp_path):
    path = tmp_path / "unsupported.txt"
    path.write_text("Hello World")
    return str(path)

from unittest.mock import MagicMock, patch
import torch

@patch('app.services.ml_service.MLService.get_model')
def test_ml_service_valid_image(mock_get_model, valid_image):
    mock_model = MagicMock()
    # Mock returning a background prediction (all class 0)
    mock_model.return_value = torch.zeros((1, 4, 384, 384), dtype=torch.float32)
    mock_get_model.return_value = mock_model

    result = MLService.analyze_image(valid_image)
    assert "defect_type" in result
    assert "confidence" in result
    assert "mask_coverage" in result
    assert "component_count" in result
    assert "largest_component_area" in result
    assert result["model_status"] == "PRODUCTION"

def test_ml_service_spatial_metrics(valid_image):
    # Mock get_model and predict to return a controlled mask
    mock_model = MagicMock()
    
    # PyTorch model outputs logits of shape (batch, classes, H, W)
    # 4 classes: 0=bg, 1=crack, 2=spall, 3=corr
    test_logits = torch.zeros((1, 4, 384, 384), dtype=torch.float32)
    
    # Default to background winning everywhere
    test_logits[0, 0, :, :] = 1.0
    
    # Noisy pixel (should be ignored since area < 50)
    test_logits[0, 1, 10, 10] = 10.0
    
    # Large block 10x10 = 100 pixels (should be counted)
    test_logits[0, 1, 50:60, 50:60] = 10.0
    
    mock_model.return_value = test_logits
    
    with patch('app.services.ml_service.MLService.get_model', return_value=mock_model):
        result = MLService.analyze_image(valid_image)
        
        # We expect 1 valid component (the 100px block)
        assert result["component_count"] == 1
        assert result["largest_component_area"] == 100
        assert result["defect_type"] == "crack"
        assert result["confidence"] == float(100) / (384 * 384)
        assert result["mask_coverage"] == float(101) / (384 * 384)

def test_ml_service_invalid_path():
    with pytest.raises(ImageProcessingError):
        MLService.analyze_image("does_not_exist.jpg")

def test_ml_service_corrupted_image(corrupted_image):
    with pytest.raises(ImageProcessingError):
        MLService.analyze_image(corrupted_image)

def test_ml_service_unsupported_image(unsupported_image):
    with pytest.raises(ImageProcessingError):
        MLService.analyze_image(unsupported_image)
