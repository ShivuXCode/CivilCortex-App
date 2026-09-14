import os
import json
import glob
import random

DATASETS_ROOT = "/Users/shivanisrimurugesan/civilcortex_project/Datasets_staging"
MANIFESTS_DIR = "/Users/shivanisrimurugesan/civilcortex_project/ml_pipeline/dataset/manifests"
REPORTS_DIR = "/Users/shivanisrimurugesan/civilcortex_project/ml_pipeline/dataset/quality_reports"

def generate_splits():
    random.seed(42)  # Deterministic seed
    
    train_manifest = []
    val_manifest = []
    test_manifest = []
    
    # Let's load the exact duplicates to avoid leaking them
    # For a real pipeline, we'd skip images that are in duplicates
    # Since duplicates calculation is running async, we will implement the group logic structurally.
    
    datasets = ["SDNET2018", "CCIC", "RC_SEGMENTATION_1841", "DAMAGE_DETECTION_2750", "MDMCS", "CICS"]
    
    split_summary = {
        "train_target_pct": 70,
        "val_target_pct": 15,
        "test_target_pct": 15,
        "actual_train_count": 0,
        "actual_val_count": 0,
        "actual_test_count": 0,
        "datasets": {}
    }

    for ds in datasets:
        ds_path = os.path.join(DATASETS_ROOT, ds)
        if not os.path.exists(ds_path):
            continue
            
        images = []
        extensions = ('*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp')
        for ext in extensions:
            images.extend(glob.glob(os.path.join(ds_path, "**", ext), recursive=True))
            images.extend(glob.glob(os.path.join(ds_path, "**", ext.upper()), recursive=True))
            
        images = list(set(images))
        images.sort() # Ensure deterministic ordering before shuffle
        
        # Group logic (Source grouping)
        if ds == "SDNET2018":
            # SDNET names files like: 7001-3.jpg (7001 is bridge deck)
            # We group by the first prefix
            groups = {}
            for img in images:
                basename = os.path.basename(img)
                # Example: C_001_1.jpg or 7001-3.jpg
                group_id = basename.split('-')[0].split('_')[0]
                groups.setdefault(group_id, []).append(img)
                
            group_keys = list(groups.keys())
            random.shuffle(group_keys)
            
            ds_train, ds_val, ds_test = 0, 0, 0
            for g in group_keys:
                r = random.random()
                if r < 0.7:
                    train_manifest.extend([{"path": p, "dataset": ds, "group_id": g} for p in groups[g]])
                    ds_train += len(groups[g])
                elif r < 0.85:
                    val_manifest.extend([{"path": p, "dataset": ds, "group_id": g} for p in groups[g]])
                    ds_val += len(groups[g])
                else:
                    test_manifest.extend([{"path": p, "dataset": ds, "group_id": g} for p in groups[g]])
                    ds_test += len(groups[g])
                    
            split_summary["datasets"][ds] = {"group_aware": True, "train": ds_train, "val": ds_val, "test": ds_test}
            
        else:
            # Random shuffle
            random.shuffle(images)
            n = len(images)
            n_train = int(n * 0.7)
            n_val = int(n * 0.15)
            
            train_manifest.extend([{"path": p, "dataset": ds, "group_id": "UNKNOWN"} for p in images[:n_train]])
            val_manifest.extend([{"path": p, "dataset": ds, "group_id": "UNKNOWN"} for p in images[n_train:n_train+n_val]])
            test_manifest.extend([{"path": p, "dataset": ds, "group_id": "UNKNOWN"} for p in images[n_train+n_val:]])
            
            split_summary["datasets"][ds] = {"group_aware": False, "train": n_train, "val": n_val, "test": n - n_train - n_val}

    split_summary["actual_train_count"] = len(train_manifest)
    split_summary["actual_val_count"] = len(val_manifest)
    split_summary["actual_test_count"] = len(test_manifest)
    
    os.makedirs(MANIFESTS_DIR, exist_ok=True)
    
    with open(os.path.join(MANIFESTS_DIR, "train_manifest.json"), "w") as f:
        json.dump(train_manifest, f)
    with open(os.path.join(MANIFESTS_DIR, "val_manifest.json"), "w") as f:
        json.dump(val_manifest, f)
    with open(os.path.join(MANIFESTS_DIR, "test_manifest.json"), "w") as f:
        json.dump(test_manifest, f)
    with open(os.path.join(REPORTS_DIR, "split_summary.json"), "w") as f:
        json.dump(split_summary, f, indent=4)
        
    print("Split generation complete.")

if __name__ == "__main__":
    generate_splits()
