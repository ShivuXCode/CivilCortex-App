import os
import pytest
from pathlib import Path
from PIL import Image
from ingestion import ingest_image, calculate_sha256

@pytest.fixture
def temp_images(tmp_path):
    # Create valid image
    valid_path = tmp_path / "valid.jpg"
    img = Image.new('RGB', (640, 640), color = 'red')
    img.save(valid_path)
    
    # Create corrupt image
    corrupt_path = tmp_path / "corrupt.jpg"
    with open(corrupt_path, "wb") as f:
        f.write(b"not an image")
        
    return valid_path, corrupt_path, tmp_path

def test_ingestion_valid(temp_images):
    valid_path, _, tmp_path = temp_images
    overrides = {
        "building_id": "bld_1"
    }
    result = ingest_image(valid_path, "civilcortex-field", overrides, output_dir=None)
    assert result["status"] == "ACCEPTED"
    assert result["sha256"] is not None
    assert result["metadata"].building_id == "bld_1"
    assert result["metadata"].image_width == 640

def test_ingestion_corrupt(temp_images):
    _, corrupt_path, tmp_path = temp_images
    overrides = {}
    result = ingest_image(corrupt_path, "civilcortex-field", overrides, output_dir=None)
    assert result["status"] == "REJECTED"
    assert "Corrupt image" in result["reason"]

def test_ingestion_unapproved_source(temp_images):
    valid_path, _, tmp_path = temp_images
    overrides = {}
    result = ingest_image(valid_path, "crack500", overrides, output_dir=None)
    assert result["status"] == "ACCEPTED"
    assert result["metadata"].production_training_eligible == False

def test_ingestion_demo_exclusion(temp_images):
    valid_path, _, tmp_path = temp_images
    overrides = {}
    result = ingest_image(valid_path, "pipeline_demo_only", overrides, output_dir=None)
    assert result["status"] == "REJECTED"
    assert "Demo data excluded" in result["reason"]

def test_sha256_exact_duplicate(temp_images):
    valid_path, _, _ = temp_images
    hash1 = calculate_sha256(valid_path)
    hash2 = calculate_sha256(valid_path)
    assert hash1 == hash2
