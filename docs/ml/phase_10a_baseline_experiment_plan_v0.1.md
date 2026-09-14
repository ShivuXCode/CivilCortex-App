# Phase 10A Baseline Experiment Plan & Field Readiness v0.1

## 1. Purpose
This document governs Track A (Public Baseline Implementation) and Track B (Field Collection Setup). The objective is to construct a reproducible ML baseline scaffolding using exclusively eligible public datasets for research, while independently solidifying the repository's ingestion framework to accept production-grade field data.

**IMPORTANT: PUBLIC BASELINES ≠ PRODUCTION MODEL.** 
No model created under this plan may be deployed as the CivilCortex production model.

## 2. Public Datasets Allowed (Research / Baseline)
- **SDNET2018**: Permitted for classification baselines only.
- **CCIC**: Permitted for controlled pretraining baselines.
- **RC1841**: Permitted for segmentation baselines.
- **DAMAGE_DETECTION**: Permitted for detection (bbox) baselines.
- **MDMCS**: Permitted for segmentation baselines.

## 3. Public Datasets Excluded
- **CICS**: Strictly excluded due to heavy overlap/duplicate pollution with SDNET2018.

## 4. Tasks Supported
- **Task A (Classification):** Does the image contain a crack? (Using SDNET2018).
- **Task B (Detection):** Where is the crack bounding box? (Using Damage Detection).
- **Task C (Segmentation):** What pixels belong to the crack? (Using RC1841, MDMCS).
- **Task D (Pretraining):** Feature learning (Using CCIC).

*No assumptions are made regarding unified multi-task models at the baseline stage.*

## 5. Dataset Provenance
Public dataset experiments must retain exact dataset versioning, image IDs, and source paths via `public_dataset_manifest.json`. Image records must not be anonymously pooled.

## 6. Leakage Controls
- pHash-based deduplication will be utilized across public datasets.
- Track B (Field Test Set) remains strictly isolated and will never overlap with public datasets. 
- Baseline split methodologies (random, phash_dedup, bridge_id) must be rigidly documented in the experiment configs.

## 7. Baseline Methodology
Baselines will use the simplest, standard architecture appropriate for the respective task (e.g., standard ResNet for classification, YOLO/FasterRCNN baseline for detection). Configuration must not be hardcoded in scripts, but loaded via JSON conforming to `baseline_config_schema.json`.

## 8. Metrics
- **Classification:** Accuracy, Precision, Recall, F1.
- **Detection:** mAP, Precision, Recall.
- **Segmentation:** IoU, Dice.

*Fake physical measurements (mm) are strictly banned for uncalibrated public baselines. Results must stay in pixel dimensions (`PIXEL_ONLY`).*

## 9. Output Contracts
Baseline inference code must emit outputs adapting to the core CivilCortex contract (`CVAnalysisResult`, `CVDetection`, `CVMeasurement`). If the model output format differs, a dedicated baseline adapter must transform it.

## 10. Field-Data Integration Plan (Track B)
The repository is primed for field data. The `ml_pipeline/dataset/` directory includes immutable `images/`, `metadata/`, `calibration/`, `manifests/`, and `splits/` folders. `readiness_checker.py` has been implemented to deterministically evaluate collected metadata against Phase 9 threshold metrics.

## 11. Limitations & What Results Can Prove
These public data experiments will only prove that our ML infrastructure functions and trains correctly (CI/CD scaffolding, metric tracking). They will **NOT** prove that the models generalize to real-world structures, nor provide measurement capabilities.
