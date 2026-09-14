# CivilCortex: Phase 2 Clean Binary Crack Classifier

This directory contains the production-ready machine learning pipeline for **image-level binary crack detection** (Crack vs. No Crack) using transfer learning with **EfficientNetB0**.

---

## 1. Directory Structure

```
ml_pipeline/
├── data/
│   ├── no_crack/             # Clean concrete/surface images (Class 0)
│   └── crack/                # Concrete crack images (Class 1)
├── preprocessing.py          # Shared preprocessing pipeline (RGB, 224x224, float32)
├── validate_dataset.py       # Dataset audit, corruption check, duplicate check
├── train_binary.py           # 2-stage transfer learning training script
├── evaluate_binary.py        # Validation threshold calibration & metrics evaluation
├── predict_binary.py         # Standalone CLI prediction utility
└── README.md
```

---

## 2. Step-by-Step Usage Guide

### Step 1: Prepare the Dataset
Place images into `ml_pipeline/data/` organized as:
```
ml_pipeline/data/
├── no_crack/
│   ├── image_001.jpg
│   └── ...
└── crack/
    ├── image_001.jpg
    └── ...
```

### Step 2: Validate Dataset Quality
```bash
python validate_dataset.py data/
```
Checks for:
- Corrupt/unreadable image files.
- Duplicate images via SHA-256 hashes.
- Class distribution and imbalance ratios.
- Resolution anomalies.

### Step 3: Train the Binary Classifier
```bash
python train_binary.py data/
```
- Performs 2-stage transfer learning using **EfficientNetB0**.
- Applies subtle data augmentation (flips, rotations, contrast) exclusively during training.
- Saves the trained model to `backend/models/crack_binary_classifier.keras`.

### Step 4: Calibrate Threshold & Evaluate
```bash
python evaluate_binary.py data/
```
- Performs a threshold sweep over validation samples to maximize F1 while prioritizing recall.
- Saves the optimal threshold to `backend/models/crack_binary_config.json`.

### Step 5: Test Single Image Inference
```bash
python predict_binary.py path/to/image.jpg
```
Output:
```
Image: sample.jpg
Prediction: CRACK
Probability: 0.9821
Threshold: 0.45
```
