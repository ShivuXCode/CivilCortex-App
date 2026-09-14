import os
import json
import hashlib
from pathlib import Path
from multiprocessing import Pool
from collections import defaultdict, Counter
from typing import Dict, Any

# Ensure we can import existing pipeline
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion import ingest_image, calculate_sha256, calculate_phash
from metadata_schema import DefectInstance

STAGING_DIR = Path("../../Datasets_staging")
METADATA_DIR = Path("metadata")
MANIFESTS_DIR = Path("manifests")
REPORTS_DIR = Path("quality_reports")

METADATA_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

DATASETS_CONFIG = {
    "SDNET2018": {
        "source_id": "sdnet2018",
        "dataset_name": "SDNET2018",
        "dataset_version": "1.0",
        "authoritative_source_url": "https://digitalcommons.usu.edu/all_datasets/48/",
        "license": "CC BY 4.0", # Based on USU Digital Commons standard, assumed for script, will be marked UNVERIFIED if uncertain
        "license_status": "UNVERIFIED",
        "production_training_eligible": True
    },
    "CCIC": {
        "source_id": "mendeley-ccic",
        "dataset_name": "Concrete Crack Images for Classification",
        "dataset_version": "1",
        "authoritative_source_url": "https://data.mendeley.com/datasets/5y9wdsg2zt/1",
        "license": "CC BY 4.0",
        "license_status": "VERIFIED",
        "production_training_eligible": True
    },
    "RC_SEGMENTATION_1841": {
        "source_id": "rc_segmentation_1841",
        "dataset_name": "Reinforced concrete structure segmentation dataset 1841",
        "dataset_version": "1",
        "authoritative_source_url": "https://data.mendeley.com/datasets/yfhwfcrfmk/1",
        "license": "CC BY 4.0",
        "license_status": "UNVERIFIED",
        "production_training_eligible": False
    },
    "DAMAGE_DETECTION_2750": {
        "source_id": "concrete_damage_2750",
        "dataset_name": "Damage Detection Dataset for Concrete Structures with Multi-Feature Backgrounds",
        "dataset_version": "1",
        "authoritative_source_url": "https://data.mendeley.com/datasets/9t3y6hhddk/1",
        "license": "CC BY 4.0",
        "license_status": "UNVERIFIED",
        "production_training_eligible": False
    },
    "MDMCS": {
        "source_id": "mdmcs_v2",
        "dataset_name": "Multi-Damage Monitoring of Concrete Structures",
        "dataset_version": "2",
        "authoritative_source_url": "https://data.mendeley.com/datasets/6x4dzzrs2h/2",
        "license": "CC BY 4.0",
        "license_status": "UNVERIFIED",
        "production_training_eligible": False
    },
    "CICS": {
        "source_id": "cics_v1",
        "dataset_name": "Cracks In Concrete Structures",
        "dataset_version": "1",
        "authoritative_source_url": "https://data.mendeley.com/datasets/9brnm3c39k/1",
        "license": "CC BY 4.0",
        "license_status": "UNVERIFIED",
        "production_training_eligible": False
    }
}

def map_cics_label(path: str):
    if "Without Crack" in path: return []
    elif "Simple Cracks" in path: return [("crack", "DIRECT", ["irregular"])]
    elif "Multibranched Crack" in path: return [("crack", "DIRECT", ["branching"])]
    return []

def process_image(args):
    img_path, ds_key = args
    cfg = DATASETS_CONFIG[ds_key]
    
    # Defaults
    defects = []
    physical_defect_identity = "UNKNOWN"
    source_group_id = None
    
    path_str = str(img_path)
    
    # Extract labels based on dataset
    if ds_key == "SDNET2018":
        # SDNET2018: paths like .../D/CD/..., D/UD/..., P/CP/..., W/CW/...
        # C = Crack, U = Uncracked
        parts = path_str.split('/')
        if 'CD' in parts or 'CP' in parts or 'CW' in parts:
            defects.append(DefectInstance(
                defect_instance_id="UNKNOWN",
                defect_type="crack",
                annotation_type="CLASSIFICATION",
                original_dataset_label="crack",
                mapping_status="DIRECT"
            ))
    elif ds_key == "CCIC":
        if "Positive" in path_str:
            defects.append(DefectInstance(
                defect_instance_id="UNKNOWN",
                defect_type="crack",
                annotation_type="CLASSIFICATION",
                original_dataset_label="Positive",
                mapping_status="DIRECT"
            ))
        source_group_id = "unavailable" # As verified, filenames don't map to the 458 source images
    elif ds_key == "CICS":
        labels = map_cics_label(path_str)
        for t, status, morphs in labels:
            defects.append(DefectInstance(
                defect_instance_id="UNKNOWN",
                defect_type=t,
                morphology_labels=morphs,
                annotation_type="CLASSIFICATION",
                original_dataset_label=Path(path_str).parent.name,
                mapping_status=status
            ))
    elif ds_key == "RC_SEGMENTATION_1841":
        # Just create an unmapped mask reference for now
        # Labeldata path
        mask_path = img_path.parent.parent / "labeldata" / (img_path.stem + ".png")
        if mask_path.exists():
            defects.append(DefectInstance(
                defect_instance_id="UNKNOWN",
                defect_type="unmapped",
                annotation_type="MASK",
                original_dataset_label="unknown",
                mapping_status="UNMAPPED",
                mask_path=str(mask_path)
            ))
    elif ds_key == "DAMAGE_DETECTION_2750":
        xml_path = img_path.parent.parent / "annot" / (img_path.stem + ".xml")
        if xml_path.exists():
            defects.append(DefectInstance(
                defect_instance_id="UNKNOWN",
                defect_type="crack", # Simplification, will need XML parsing for spalling/etc
                annotation_type="BBOX",
                original_dataset_label="parsed_from_xml",
                mapping_status="PARTIAL",
                original_annotation_path=str(xml_path)
            ))
    elif ds_key == "MDMCS":
        defects.append(DefectInstance(
            defect_instance_id="UNKNOWN",
            defect_type="unmapped",
            annotation_type="MASK",
            original_dataset_label="unknown",
            mapping_status="UNMAPPED"
        ))

    metadata_overrides = {
        "dataset_version": cfg["dataset_version"],
        "license": cfg["license"],
        "license_status": cfg["license_status"],
        "provenance_status": "VALID",
        "production_training_eligible": cfg["production_training_eligible"],
        "defects": [d.model_dump() for d in defects]
    }
    
    result = ingest_image(img_path, cfg["source_id"], metadata_overrides, METADATA_DIR)
    
    manifest_entry = {
        "source_id": cfg["source_id"],
        "source_dataset_name": cfg["dataset_name"],
        "dataset_version": cfg["dataset_version"],
        "image_id": result.get("metadata").image_id if result.get("metadata") else None,
        "original_path": str(img_path),
        "filename": img_path.name,
        "extension": img_path.suffix,
        "sha256": result.get("sha256"),
        "phash": result.get("phash"),
        "physical_defect_identity": physical_defect_identity,
        "source_group_id": source_group_id,
        "license_status": cfg["license_status"],
        "provenance_status": "VALID" if result["status"] == "ACCEPTED" else "INVALID",
        "quality_status": "PENDING"
    }
    
    return manifest_entry

if __name__ == "__main__":
    print("Gathering images...")
    tasks = []
    
    extensions = {'.jpg', '.jpeg', '.png'}
    
    for ds_key in DATASETS_CONFIG.keys():
        ds_dir = STAGING_DIR / ds_key
        if not ds_dir.exists():
            print(f"Skipping {ds_key}, dir not found")
            continue
        for root, _, files in os.walk(ds_dir):
            for f in files:
                if Path(f).suffix.lower() in extensions:
                    tasks.append((Path(root) / f, ds_key))
                    
    print(f"Found {len(tasks)} images. Ingesting...")
    
    manifests = []
    
    # Process sequentially for the first few to debug, then multiprocess
    with Pool(os.cpu_count()) as pool:
        for i, res in enumerate(pool.imap_unordered(process_image, tasks, chunksize=100)):
            manifests.append(res)
            if (i+1) % 5000 == 0:
                print(f"Processed {i+1}/{len(tasks)}")
                
    # Duplicate Analysis
    print("Performing cross-dataset duplicate analysis...")
    sha256_groups = defaultdict(list)
    for m in manifests:
        if m["sha256"]:
            sha256_groups[m["sha256"]].append(m)
            
    exact_duplicates = 0
    cross_dataset_overlaps = 0
    
    for h, group in sha256_groups.items():
        if len(group) > 1:
            exact_duplicates += (len(group) - 1)
            sources = set(m["source_id"] for m in group)
            if len(sources) > 1:
                cross_dataset_overlaps += 1
                
    with open(MANIFESTS_DIR / "full_manifest.json", "w") as f:
        json.dump(manifests, f, indent=4)
        
    print(f"Done. Exact dups: {exact_duplicates}, Cross overlaps: {cross_dataset_overlaps}")
