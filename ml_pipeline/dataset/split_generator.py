import json
import random
from pathlib import Path
from collections import defaultdict
from metadata_schema import ImageMetadata

def get_grouping_key(img: ImageMetadata) -> str:
    """
    Determines the most encompassing grouping key to prevent leakage.
    Hierarchy: building_id -> site_id -> inspection_id -> defect_instance_id -> image_id.
    This guarantees that images of the same physical crack or from the same building
    do not cross splits if higher-level metadata is available.
    """
    if img.building_id:
        return f"bld_{img.building_id}"
    if img.site_id:
        return f"site_{img.site_id}"
    if img.inspection_id:
        return f"insp_{img.inspection_id}"
    if img.defects:
        # Group by the first defect instance if no higher context exists
        return f"def_{img.defects[0].defect_instance_id}"
    
    # Fallback to image isolation
    return f"img_{img.image_id}"

def generate_splits(metadata_dir: str, seed: int = 42):
    random.seed(seed)
    p = Path(metadata_dir)
    
    # Group images by their hierarchical key
    groups = defaultdict(list)
    total_images = 0
    
    if p.exists():
        for json_file in p.glob("*.json"):
            with open(json_file, 'r') as f:
                data = json.load(f)
                img = ImageMetadata(**data)
                if img.quality_status == "PASS":
                    gkey = get_grouping_key(img)
                    groups[gkey].append(img.image_id)
                    total_images += 1
    
    # Determine split sizes (70% train, 15% val, 15% test)
    # We assign whole groups to splits to ensure leakage prevention
    group_keys = list(groups.keys())
    random.shuffle(group_keys)
    
    train_ids, val_ids, test_ids = [], [], []
    train_count, val_count = 0, 0
    
    target_train = total_images * 0.70
    target_val = total_images * 0.15
    
    for gkey in group_keys:
        imgs = groups[gkey]
        if train_count < target_train:
            train_ids.extend(imgs)
            train_count += len(imgs)
        elif val_count < target_val:
            val_ids.extend(imgs)
            val_count += len(imgs)
        else:
            test_ids.extend(imgs)
            
    manifest = {
        "seed": seed,
        "total_images": total_images,
        "isolation_strategy": "hierarchical (building_id > site_id > inspection_id > defect_instance_id)",
        "splits": {
            "train": train_ids,
            "val": val_ids,
            "test": test_ids
        }
    }
    
    with open(p.parent / "manifests" / "split_manifest.json", "w") as f:
        json.dump(manifest, f, indent=4)
    
    print(f"Generated splits: {len(train_ids)} train, {len(val_ids)} val, {len(test_ids)} test.")
    return manifest

if __name__ == "__main__":
    generate_splits("metadata")
