# Phase 10E-0: Public-Data Training and Architecture Benchmark Plan v0.1

## 1. Objective
Establish reproducible experimental infrastructure and execute controlled baseline model training using the audited public datasets (SDNET2018, DAMAGE_DETECTION, RC1841). This phase validates the pipeline at scale and provides architecture insights before field data is integrated.

## 2. Distinction from Previous Phases
- **Previous:** 1-epoch tiny-sample experiments were strictly PIPELINE SMOKE TESTS and did not measure model performance.
- **This Phase:** Real development-scale experiments.
- **Final Training:** Blocked until Phase 10E real field data is collected.

## 3. Dataset Usage and Subsets
- **SDNET2018**: Classification baseline. To manage computational load, a fixed, reproducible, and stratified 10% subset (~5,600 images) is used.
- **DAMAGE_DETECTION**: Detection baseline using bounding boxes. Full dataset (~2,750 images).
- **RC1841**: Segmentation baseline. Full dataset (~1,841 images).
- **MDMCS**: Explicitly **EXCLUDED** due to a missing dataset adapter and unverified licensing restrictions.
- **CCIC/CICS**: Pretraining or excluded as per Phase 9.5 audit.

## 4. Initial Experiments
- **EXP-A**: SDNET2018 | Classification | ResNet-18 (10% subset)
- **EXP-B**: SDNET2018 | Classification | ResNet-50 (10% subset)
- **EXP-C**: DAMAGE_DETECTION | Object Detection | Faster R-CNN
- **EXP-D**: RC1841 | Segmentation | FCN

## 5. Metrics and Evaluation
- **Classification**: Accuracy, Precision, Recall, F1
- **Detection**: mAP, Precision, Recall
- **Segmentation**: IoU, Dice/F1, Precision, Recall

## 6. Device Support
The pipeline dynamically selects MPS (if available), CUDA, or CPU. MPS is disabled for detection models (Faster R-CNN) if it causes known hangs, falling back safely to CPU.

## 7. Data Leakage Prevention
Checksum and pHash analysis from Phase 8 are utilized to prevent exact and near-duplicates from crossing train/val/test boundaries. If public datasets lack building metadata, building-level generalization is explicitly noted as impossible to establish.

## 8. Artifact Generation
All results are deterministically saved in `ml_pipeline/baselines/experiments/<experiment_id>/` and contain:
- `config.json`
- `metrics.json`
- `train_manifest.json`
- `validation_manifest.json`
- `training_history.json`
- `best_checkpoint.meta`
