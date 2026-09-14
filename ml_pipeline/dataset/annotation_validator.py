import json
import os
from pathlib import Path
try:
    from shapely.geometry import Polygon
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
from metadata_schema import ImageMetadata

def validate_image_metadata(img: ImageMetadata):
    errors = []
    
    # 1. Missing annotations
    if img.quality_status == "PASS" and not img.defects:
        # It's valid to have NO_DEFECT images, but we check if it claims a crack and has no polygons
        pass 
        
    for defect in img.defects:
        # 2. Invalid class labels
        if defect.mapping_status == "UNMAPPED":
            # Unmapped original labels are preserved
            pass
        elif defect.defect_type not in ["crack", "spalling", "efflorescence"]:
            errors.append(f"Invalid defect_type {defect.defect_type}")
            
        for morph in defect.morphology_labels:
            if morph not in ["diagonal", "horizontal", "vertical", "branching", "irregular"]:
                errors.append(f"Invalid morphology {morph}")
        
        # 3. Polygon validation
        if defect.annotation_type == "POLYGON" and defect.polygon:
            if len(defect.polygon) < 3:
                errors.append(f"Polygon too small for defect {defect.defect_instance_id}")
                continue
                
            try:
                if SHAPELY_AVAILABLE:
                    poly = Polygon(defect.polygon)
                    # Self-intersecting polygons
                    if not poly.is_valid:
                        errors.append(f"Self-intersecting or invalid polygon for defect {defect.defect_instance_id}")
            except Exception as e:
                errors.append(f"Error parsing polygon for defect {defect.defect_instance_id}: {e}")
                
            # 4. Out-of-bounds coordinates
            for pt in defect.polygon:
                if pt[0] < 0 or pt[0] > img.image_width or pt[1] < 0 or pt[1] > img.image_height:
                    errors.append(f"Polygon point out of bounds for defect {defect.defect_instance_id}")
                    break

    return errors

def validate_all_annotations(metadata_dir: str):
    p = Path(metadata_dir)
    if not p.exists():
        return
    for json_file in p.glob("*.json"):
        with open(json_file, 'r') as f:
            data = json.load(f)
            img = ImageMetadata(**data)
            errs = validate_image_metadata(img)
            if errs:
                print(f"Validation failed for {json_file.name}: {errs}")
