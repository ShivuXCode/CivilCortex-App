import json
import os
from pathlib import Path

REPORTS_DIR = Path("quality_reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def generate_corrected_report():
    report = {
        "datasets_discovered": [
            "SDNET2018",
            "Concrete Crack Images for Classification",
            "Reinforced concrete structure segmentation dataset 1841",
            "Damage Detection Dataset for Concrete Structures with Multi-Feature Backgrounds",
            "Multi-Damage Monitoring of Concrete Structures",
            "Cracks In Concrete Structures"
        ],
        "datasets_ingested": [
            "SDNET2018",
            "Concrete Crack Images for Classification",
            "Reinforced concrete structure segmentation dataset 1841",
            "Damage Detection Dataset for Concrete Structures with Multi-Feature Backgrounds",
            "Multi-Damage Monitoring of Concrete Structures",
            "Cracks In Concrete Structures"
        ],
        "datasets_partial_failed": [],
        "image_counts": {
            "total_raw_image_count": 113883,
            "total_valid_image_count": 113883,
            "classification_labeled_image_count": 108092, # 56092 + 40000 + 12000
            "bbox_annotated_image_count": 2750,
            "mask_annotated_image_count": 3041, # 1841 + 1200
            "polygon_annotated_image_count": 0,
            "images_with_any_annotation": 113883,
            "images_without_annotation": 0,
            "malformed_annotation_count": 0
        },
        "dataset_annotation_breakdown": [
            {"dataset": "SDNET2018", "total": 56092, "classification": 56092, "bbox": 0, "mask": 0, "polygon": 0, "other": 0, "none": 0, "malformed": 0},
            {"dataset": "Concrete Crack Images for Classification", "total": 40000, "classification": 40000, "bbox": 0, "mask": 0, "polygon": 0, "other": 0, "none": 0, "malformed": 0},
            {"dataset": "Reinforced concrete structure segmentation dataset 1841", "total": 1841, "classification": 0, "bbox": 0, "mask": 1841, "polygon": 0, "other": 0, "none": 0, "malformed": 0},
            {"dataset": "Damage Detection Dataset for Concrete Structures with Multi-Feature Backgrounds", "total": 2750, "classification": 0, "bbox": 2750, "mask": 0, "polygon": 0, "other": 0, "none": 0, "malformed": 0},
            {"dataset": "Multi-Damage Monitoring of Concrete Structures", "total": 1200, "classification": 0, "bbox": 0, "mask": 1200, "polygon": 0, "other": 0, "none": 0, "malformed": 0},
            {"dataset": "Cracks In Concrete Structures", "total": 12000, "classification": 12000, "bbox": 0, "mask": 0, "polygon": 0, "other": 0, "none": 0, "malformed": 0}
        ],
        "duplicate_analysis": {
            "exact_duplicates_within_dataset": 8464,
            "exact_duplicates_across_datasets": 651,
            "near_duplicates_within_dataset": "NOT_RUN",
            "near_duplicates_across_datasets": "NOT_RUN",
            "source_derived_relationships": "UNAVAILABLE",
            "uncertain_overlap_groups": "NOT_RUN"
        },
        "ccic_source_mapping": {
            "source_mapping_status": "UNAVAILABLE",
            "source_image_count": 458,
            "note": "CCIC filenames and folder structure prevent deterministic mapping back to the known 458 source images."
        },
        "license_reporting": [
            {
                "dataset": "SDNET2018",
                "authoritative_source": "https://digitalcommons.usu.edu/all_datasets/48/",
                "version": "1.0",
                "license": "CC BY 4.0",
                "license_verification_status": "UNVERIFIED",
                "commercial_use_status": "UNKNOWN",
                "production_training_eligible": False
            },
            {
                "dataset": "Concrete Crack Images for Classification",
                "authoritative_source": "https://data.mendeley.com/datasets/5y9wdsg2zt/1",
                "version": "1",
                "license": "CC BY 4.0",
                "license_verification_status": "VERIFIED",
                "commercial_use_status": "ALLOWED",
                "production_training_eligible": False
            },
            {
                "dataset": "Reinforced concrete structure segmentation dataset 1841",
                "authoritative_source": "https://data.mendeley.com/datasets/yfhwfcrfmk/1",
                "version": "1",
                "license": "CC BY 4.0",
                "license_verification_status": "UNVERIFIED",
                "commercial_use_status": "UNKNOWN",
                "production_training_eligible": False
            },
            {
                "dataset": "Damage Detection Dataset for Concrete Structures with Multi-Feature Backgrounds",
                "authoritative_source": "https://data.mendeley.com/datasets/9t3y6hhddk/1",
                "version": "1",
                "license": "CC BY 4.0",
                "license_verification_status": "UNVERIFIED",
                "commercial_use_status": "UNKNOWN",
                "production_training_eligible": False
            },
            {
                "dataset": "Multi-Damage Monitoring of Concrete Structures",
                "authoritative_source": "https://data.mendeley.com/datasets/6x4dzzrs2h/2",
                "version": "2",
                "license": "CC BY 4.0",
                "license_verification_status": "UNVERIFIED",
                "commercial_use_status": "UNKNOWN",
                "production_training_eligible": False
            },
            {
                "dataset": "Cracks In Concrete Structures",
                "authoritative_source": "https://data.mendeley.com/datasets/9brnm3c39k/1",
                "version": "1",
                "license": "CC BY 4.0",
                "license_verification_status": "UNVERIFIED",
                "commercial_use_status": "UNKNOWN",
                "production_training_eligible": False
            }
        ],
        "taxonomy_coverage": {
            "crack": 108092, # Estimated total with crack mapped
            "spalling": "UNMAPPED",
            "efflorescence": 0,
            "corrosion": "UNMAPPED",
            "exposed_rebar": "UNMAPPED",
            "crushing": "UNMAPPED",
            "deformation": "UNMAPPED",
            "surface_deterioration": "UNMAPPED"
        },
        "spalling_matrix": {
            "dataset_contains_spalling_images": True,
            "dataset_has_spalling_classification_labels": False,
            "dataset_has_spalling_bounding_boxes": True,
            "dataset_has_spalling_masks": True,
            "dataset_has_validated_instance_level_spalling_annotations": False
        },
        "efflorescence_coverage": {
            "efflorescence_source_coverage": 0,
            "efflorescence_production_readiness": "FAIL"
        },
        "calibration": "UNAVAILABLE",
        "hierarchy": {
            "public_dataset_hierarchy_coverage": "LIMITED / FAIL"
        },
        "longitudinal_monitoring": "FAIL",
        "pytest_status": {
            "pytest_status": "NOT_EXECUTED",
            "reason": "pytest executable/dependency unavailable. The system prohibits automated installation of Python packages, and no existing virtual environment containing pytest (.venv, pip, poetry, uv, etc.) was found."
        },
        "dataset_acceptance_status": "FAIL / BLOCKED"
    }
    
    with open(REPORTS_DIR / "dataset_audit_report_v0.1_corrected.json", "w") as f:
        json.dump(report, f, indent=4)
        
    md_content = """# CivilCortex Phase 7D Dataset Audit Report v0.1 (Corrected)

## Executive Summary
This report summarizes the corrected dataset ingestion and provenance audit for the six external datasets.
No ML models were trained. Original data remained immutable. All missing metrics are explicitly reported as NOT_RUN or UNAVAILABLE rather than defaulting to zero.

## A. Datasets Discovered
SDNET2018, Concrete Crack Images for Classification (CCIC), Reinforced concrete structure segmentation dataset 1841, Damage Detection Dataset for Concrete Structures with Multi-Feature Backgrounds, Multi-Damage Monitoring of Concrete Structures (MDMCS), Cracks In Concrete Structures (CICS)

## B. Datasets Ingested
All 6 discovered datasets were successfully ingested.

## C. Datasets Partial/Failed
None

## D. File Discovery and Mappings

### Annotation Breakdown
| Dataset | Total Images | Classification | BBox | Mask | Polygon | Other | No Annotation | Malformed |
|---|---|---|---|---|---|---|---|---|
| SDNET2018 | 56,092 | 56,092 | 0 | 0 | 0 | 0 | 0 | 0 |
| CCIC | 40,000 | 40,000 | 0 | 0 | 0 | 0 | 0 | 0 |
| RC Segmentation 1841 | 1,841 | 0 | 0 | 1,841 | 0 | 0 | 0 | 0 |
| Damage Detection 2750 | 2,750 | 0 | 2,750 | 0 | 0 | 0 | 0 | 0 |
| MDMCS | 1,200 | 0 | 0 | 1,200 | 0 | 0 | 0 | 0 |
| CICS | 12,000 | 12,000 | 0 | 0 | 0 | 0 | 0 | 0 |
**Total**: 113,883 Valid Images

### MDMCS Count Correction
MDMCS contains exactly 1,200 unique original images (`train_image`: 1000, `val_image`: 100, `test_image`: 100). The previously reported 2,500 count incorrectly included derived mask PNG files as original images.

### CCIC Source Mapping
`source_mapping_status = UNAVAILABLE`
CCIC filenames (`00001.jpg` to `20000.jpg` per class) and structure prevent deterministic mapping back to the known 458 source images. The count of 40,000 does NOT equate to 40,000 independent physical defects.

## E. Cross-Dataset Overlap Audit
- `exact_duplicates_within_dataset`: 8,464
- `exact_duplicates_across_datasets`: 651
- `near_duplicates_within_dataset`: NOT_RUN
- `near_duplicates_across_datasets`: NOT_RUN
- `source_derived_relationships`: UNAVAILABLE
- `uncertain_overlap_groups`: NOT_RUN

*Note: Near-duplicate analysis was not executed because the required imagehash/pHash processing dependency was unavailable or unsuitable for the current processing environment. A value of zero must not be inferred.*

## F. License Status
- SDNET2018: UNVERIFIED (CC BY 4.0). `production_training_eligible = False`
- CCIC: VERIFIED (CC BY 4.0). Commercial Use: ALLOWED. `production_training_eligible = False` (Due to leakage risks)
- RC 1841: UNVERIFIED (CC BY 4.0). `production_training_eligible = False`
- Damage Detection 2750: UNVERIFIED (CC BY 4.0). `production_training_eligible = False`
- MDMCS: UNVERIFIED (CC BY 4.0). `production_training_eligible = False`
- CICS: UNVERIFIED (CC BY 4.0). `production_training_eligible = False`

## G. Taxonomy Coverage
CivilCortex primary classes are mapped directly; unsupported source labels are marked UNMAPPED and preserved natively.
- crack: ~108,092 Classification labels (plus bounding boxes and masks)
- spalling: UNMAPPED
- efflorescence: 0
- corrosion: UNMAPPED
- exposed_rebar: UNMAPPED
- crushing: UNMAPPED
- deformation: UNMAPPED
- surface_deterioration: UNMAPPED

## H. Spalling Coverage Matrix
- dataset_contains_spalling_images: True
- dataset_has_spalling_classification_labels: False
- dataset_has_spalling_bounding_boxes: True
- dataset_has_spalling_masks: True
- dataset_has_validated_instance_level_spalling_annotations: False

## I. Efflorescence Coverage
- `efflorescence_source_coverage = 0`
- `efflorescence_production_readiness = FAIL`

## J. Calibration
`CALIBRATION = UNAVAILABLE` (PIXEL_ONLY measurements; physical calibrations are missing).

## K. Hierarchy
`public_dataset_hierarchy_coverage = LIMITED / FAIL`

## L. Longitudinal Monitoring
`LONGITUDINAL DATA = FAIL`

## M. Leakage Risks
HIGH. 651 exact cross-dataset overlaps exist. Unknown number of near-duplicates (since analysis was NOT_RUN). CCIC grouping is unavailable.

## N. Test Execution
`pytest_status = NOT_EXECUTED`
Reason: pytest executable/dependency unavailable. The system prohibits automated installation of Python packages, and no existing virtual environment containing pytest (.venv, pip, poetry, uv, etc.) was found.

## O. Dataset Acceptance Status
`FAIL / BLOCKED`
Production training readiness remains FAIL. The public datasets lack verified production licensing, reliable hierarchy, calibrated data, and longitudinal insights.

## P. Recommended Next Phase
Model Selection & Benchmark Planning (Restricted to Research/Pre-training only), coupled with Human Field Data Collection planning for the remaining gaps.
"""
    with open(REPORTS_DIR / "dataset_audit_report_v0.1_corrected.md", "w") as f:
        f.write(md_content)
        
    print("Corrected report generated.")

if __name__ == "__main__":
    generate_corrected_report()
