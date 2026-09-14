import hashlib
import json
from pathlib import Path
from PIL import Image
try:
    import imagehash
except ImportError:
    imagehash = None

from metadata_schema import ImageMetadata, CalibrationData

APPROVED_PRODUCTION_SOURCES = ["civilcortex-field", "deepcrack", "sdnet2018", "mendeley-ccic"]

def calculate_sha256(filepath: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def calculate_phash(filepath: Path) -> str:
    if not imagehash:
        return "phash_unavailable"
    try:
        img = Image.open(filepath)
        return str(imagehash.phash(img))
    except Exception:
        return "phash_error"

def ingest_image(
    filepath: Path,
    source_id: str,
    metadata_overrides: dict,
    output_dir: Path
) -> dict:
    result = {
        "status": "REJECTED",
        "reason": "",
        "metadata": None,
        "sha256": None,
        "phash": None
    }
    
    # 1. Source verification
    production_eligible = source_id.lower() in APPROVED_PRODUCTION_SOURCES
    
    if source_id.lower() == "pipeline_demo_only":
        result["reason"] = "Demo data excluded from production pipeline."
        return result
        
    # 2. File verification
    if not filepath.exists() or not filepath.is_file():
        result["reason"] = "File not found or not a valid file."
        return result
        
    try:
        with Image.open(filepath) as img:
            img.verify()
    except Exception as e:
        result["reason"] = f"Corrupt image file: {e}"
        return result
        
    # 3. Hashing
    sha256 = calculate_sha256(filepath)
    phash = calculate_phash(filepath)
    
    result["sha256"] = sha256
    result["phash"] = phash
    
    # 4. Construct metadata
    with Image.open(filepath) as img:
        width, height = img.size
        
    base_metadata = {
        "image_id": filepath.stem,
        "source_id": source_id,
        "image_width": width,
        "image_height": height,
        "quality_status": "PENDING",
        "production_training_eligible": production_eligible
    }
    
    # Merge overrides (must contain required fields)
    base_metadata.update(metadata_overrides)
    
    try:
        metadata = ImageMetadata(**base_metadata)
    except Exception as e:
        result["reason"] = f"Metadata schema validation failed: {e}"
        return result
        
    # 5. Output
    if output_dir:
        out_path = output_dir / f"{metadata.image_id}.json"
        with open(out_path, "w") as f:
            f.write(metadata.model_dump_json(indent=4))
            
    result["status"] = "ACCEPTED"
    result["metadata"] = metadata
    return result
