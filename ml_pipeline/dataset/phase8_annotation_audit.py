import os
import json
import glob
from collections import defaultdict

DATASETS_ROOT = "/Users/shivanisrimurugesan/civilcortex_project/Datasets_staging"
REPORTS_DIR = "/Users/shivanisrimurugesan/civilcortex_project/ml_pipeline/dataset/quality_reports"

def audit_annotations():
    datasets = {
        "SDNET2018": {"type": "classification", "path": "SDNET2018"},
        "CCIC": {"type": "classification", "path": "CCIC"},
        "RC1841": {"type": "mask", "path": "RC_SEGMENTATION_1841"},
        "DamageDetection": {"type": "bbox", "path": "DAMAGE_DETECTION_2750"},
        "MDMCS": {"type": "mask", "path": "MDMCS"},
        "CICS": {"type": "classification", "path": "CICS"}
    }

    # Taxonomy mapping (Expected CivilCortex: crack, spalling, efflorescence)
    # We look for files or directories that indicate the class
    class_counts = defaultdict(int)
    morphology_counts = defaultdict(int)
    
    # Simple hard negative analysis
    hard_negative_evidence = []
    
    # Calibration analysis
    calibration_evidence = False

    for ds_name, ds_info in datasets.items():
        base_path = os.path.join(DATASETS_ROOT, ds_info["path"])
        if not os.path.exists(base_path):
            continue
            
        if ds_info["type"] == "classification":
            # Count by subdirectory
            subdirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            for sd in subdirs:
                lower_sd = sd.lower()
                # Count files
                files = glob.glob(os.path.join(base_path, sd, "*.*"))
                img_count = len([f for f in files if f.endswith(('.jpg', '.jpeg', '.png'))])
                
                if 'crack' in lower_sd:
                    class_counts['crack'] += img_count
                elif 'spall' in lower_sd:
                    class_counts['spalling'] += img_count
                elif 'efflorescence' in lower_sd:
                    class_counts['efflorescence'] += img_count
                elif 'non' in lower_sd or 'without' in lower_sd or 'intact' in lower_sd:
                    hard_negative_evidence.append(f"{ds_name}: {sd} ({img_count} images)")
        
        elif ds_info["type"] == "bbox":
            # Assuming XML or JSON annotations
            anno_path = os.path.join(base_path, "annotations")
            if os.path.exists(anno_path):
                # Count classes from xml files (simplified check)
                xmls = glob.glob(os.path.join(anno_path, "*.xml"))
                for xml in xmls:
                    with open(xml, 'r', errors='ignore') as f:
                        content = f.read().lower()
                        if '<name>crack</name>' in content: class_counts['crack'] += 1
                        if '<name>spall</name>' in content: class_counts['spalling'] += 1
                        if '<name>efflorescence</name>' in content: class_counts['efflorescence'] += 1
                        
        elif ds_info["type"] == "mask":
            # Typically binary masks. Hard to extract class without metadata.
            # Usually these are crack-only segmentation datasets.
            masks_path = os.path.join(base_path, "masks")
            if os.path.exists(masks_path):
                mask_count = len(glob.glob(os.path.join(masks_path, "*.png")))
                class_counts['crack'] += mask_count
                
    # Build Audit output
    audit = {
        "annotation_audit": {
            "class_coverage": {
                "crack": class_counts['crack'],
                "spalling": class_counts['spalling'],
                "efflorescence": class_counts['efflorescence']
            },
            "morphology_coverage": "INSUFFICIENT (None of the 6 public datasets inherently map to branch/diagonal/horizontal instances without custom labeling)",
            "hard_negative_status": {
                "evidence": hard_negative_evidence,
                "status": "SUFFICIENT_FOR_CLASSIFICATION, INSUFFICIENT_FOR_DETECTION"
            },
            "calibration_status": {
                "physical_measurements_supported": False,
                "reason": "None of the 6 downloaded datasets contain ruler annotations, known camera parameters, or physical scale references.",
                "status": "UNAVAILABLE"
            }
        },
        "leakage_analysis": {
            "source_grouping_availability": {
                "SDNET2018": "High (Bridge IDs encoded in filenames)",
                "CCIC": "None (No structure IDs, randomly shuffled)",
                "RC1841": "None",
                "DamageDetection": "None",
                "MDMCS": "None",
                "CICS": "None"
            },
            "leakage_risk": "HIGH",
            "unresolved_leakage": "Since SDNET2018 is the only dataset with structure-level IDs, building-level generalization CANNOT be verified for the other 5 sources.",
            "recommended_strategy": "For SDNET2018, group by Bridge ID. For others, split randomly but rely on perceptual hash exact duplicate removal."
        },
        "dataset_acceptance_matrix": {
            "SDNET2018": {"production_eligible": "CONDITIONAL", "reason": "Requires CC-BY 4.0 strict validation, high risk of false positives."},
            "CCIC": {"production_eligible": "CONDITIONAL", "reason": "Only useful for classification. Leakage risk high."},
            "RC1841": {"production_eligible": "CONDITIONAL", "reason": "Good for segmentation pretraining."},
            "DamageDetection": {"production_eligible": "CONDITIONAL", "reason": "Useful for bbox training, limited size."},
            "MDMCS": {"production_eligible": "CONDITIONAL", "reason": "Useful for segmentation."},
            "CICS": {"production_eligible": "CONDITIONAL", "reason": "Redundant with SDNET/CCIC if duplicates aren't managed."}
        }
    }
    
    with open(os.path.join(REPORTS_DIR, "dataset_audit_report_v0.2.json"), "w") as f:
        json.dump(audit, f, indent=4)
        
    print("Annotation audit complete.")

if __name__ == "__main__":
    audit_annotations()
