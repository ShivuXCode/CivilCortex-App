# CivilCortex Split Strategy v0.1

## Overview
A random 70/15/15 split across the aggregated 113,883 image dataset would guarantee severe data leakage. To prevent the model from memorizing the background textures of specific structures, the split strategy must be group-aware.

## 1. Group-Aware Splitting
The `phase8_split_generator.py` script prioritizes structural boundaries over image boundaries:
- **SDNET2018**: Contains Bridge IDs in the filename (e.g., `7001-3.jpg` is Bridge Deck 7001). The script parses this ID and groups all images from the same bridge into the same split (Train, Val, or Test).
- **Other Datasets**: CCIC, CICS, and MDMCS do not provide inherent structural IDs. They are treated as `UNKNOWN` groups. For these, we fallback to random splitting but rely strictly on the Perceptual Hash analysis to purge exact and near-duplicates across splits.

## 2. Split Targets
- **Train (70%)**: Used for gradient descent.
- **Validation (15%)**: Used for hyperparameter tuning and early stopping.
- **Test (15%)**: Strictly frozen. Never viewed by the model or hyperparameter search.

## 3. Implementation
The generator outputs three deterministic files: `train_manifest.json`, `val_manifest.json`, and `test_manifest.json`. The generator uses a fixed random seed (`42`) to ensure reproducibility. Any duplicate images flagged by the `duplicate_clusters.json` report must be actively purged from these manifests before training begins.
