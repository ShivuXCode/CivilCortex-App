# Phase 10B: Public Dataset Baseline Results v0.1

**STATUS:** COMPLETE
**VERDICT:** BASELINE PIPELINE VERIFIED

> [!IMPORTANT]
> The metrics and losses reported in this document are derived from PIPELINE SMOKE TESTS (1 epoch, minimal samples). They are NOT performance benchmarks. Do NOT infer model quality, generalization, thin-crack performance, or field-data requirements from these numbers.

## 1. Objective
The goal of Phase 10B was to verify the ML baseline framework by executing the first reproducible PyTorch pipelines using the public datasets approved in Phase 9.5. This phase tests the dataset adapters, environment configuration, and training loops for the core CV tasks (classification, object detection, and semantic segmentation) without engaging in full-scale production model training.

## 2. Methodology
Three baseline scripts were implemented in `ml_pipeline/baselines/scripts/`:
- `train_classification.py`
- `train_detection.py`
- `train_segmentation.py`

Each script utilizes a standard baseline architecture (ResNet18, Faster R-CNN, FCN) solely to validate that the data loading and gradient calculation steps complete without errors.

### Dataset Adapter Engineering Results
Before implementation, the local dataset structures were audited:
- **SDNET2018 (Classification):** Verified as a nested directory structure (`D/CD`, `D/UD`, etc.) containing JPG images. Handled via a custom directory-traversal PyTorch Dataset.
- **Damage Detection 2750 (Detection):** Verified as a Pascal VOC-like structure (`img/` containing PNG/JPG images and `annot/` containing XML bounding box annotations).
- **RC1841 (Segmentation):** Verified as LabelMe JSON files containing polygon points, NOT pre-rendered PNG masks. The adapter uses `PIL.ImageDraw` to dynamically render semantic masks during the data loading step.

## 3. Smoke Test Execution Results

All three baseline pipelines executed successfully, completing a single epoch over a tiny subset of the data. 

### Experiment 1: Classification
- **Dataset:** SDNET2018
- **Architecture:** ResNet18 (Baseline Implementation Only)
- **Task:** Binary Crack Classification
- **Hardware:** MPS (Apple Silicon GPU)
- **Result:** **PASS**
- **Metrics (PIPELINE SMOKE TEST — NOT A PERFORMANCE BENCHMARK):**
  - Loss (1 epoch, 100 samples): 0.4414
  - Execution Time: 9.99 seconds

### Experiment 2: Semantic Segmentation
- **Dataset:** RC1841
- **Architecture:** FCN-ResNet50 (Baseline Implementation Only)
- **Task:** Binary Crack Segmentation (Mask rendering from polygons)
- **Hardware:** MPS (Apple Silicon GPU)
- **Result:** **PASS**
- **Metrics (PIPELINE SMOKE TEST — NOT A PERFORMANCE BENCHMARK):**
  - Loss (1 epoch, 30 samples): 0.4406
  - Execution Time: 20.37 seconds

### Experiment 3: Object Detection
- **Dataset:** Damage Detection 2750
- **Architecture:** Faster R-CNN ResNet50 FPN V2 (Baseline Implementation Only)
- **Task:** Damage Bounding Box Detection
- **Hardware:** CPU (MPS execution hung due to torchvision RoIAlign/NMS incompatibility on this environment)
- **Result:** **PASS**
- **Metrics (PIPELINE SMOKE TEST — NOT A PERFORMANCE BENCHMARK):**
  - Loss (1 epoch, 50 samples): 0.9268
  - Execution Time: 349.75 seconds

## 4. Pipeline Vulnerabilities & Observations
1. **Heterogeneous Formats:** The public datasets exhibit high variance in annotation schemas (directory flags, XML VOC boxes, JSON polygons). Any future data curation must standardize into a uniform format (e.g., COCO JSON) to prevent adapter overhead.
2. **Hardware Constraints:** `torchvision` object detection models exhibit silent hangs on macOS MPS backend during certain operations (like Non-Maximum Suppression). Production pipelines must defensively fall back to CPU or be executed on CUDA environments to guarantee stability.
3. **Empty Annotations:** Object detection pipelines will encounter `NaN` losses if images have zero bounding boxes and aren't handled correctly during the batching step.

## 5. Next Steps
The pipeline is formally verified to run end-to-end on public data. We are now unblocked to proceed to **Phase 10C: Data-Driven Architecture Selection + Field-Data Integration Planning**.
