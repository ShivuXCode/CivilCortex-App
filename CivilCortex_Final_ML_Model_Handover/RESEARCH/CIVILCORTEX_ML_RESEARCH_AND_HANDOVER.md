# CIVILCORTEX ML RESEARCH & MODEL HANDOVER

## 1. ML Objective
The objective of this machine learning phase is **pixel-wise structural damage segmentation**. The model takes an RGB image as input and produces a semantic mask detailing defect localization, defect type (Crack, Spalling, Corrosion), and spatial/geometric information. 

**Critical Distinction**: The ML segmentation output isolates visual defects. It **does not** determine engineering severity, structural integrity, or provide engineering recommendations. Downstream engineering assessment requires additional context (scale, load, material properties) beyond pixel localization.

## 2. All Datasets Discovered
During exploratory research, six datasets were discovered and evaluated for their usability in training a segmentation model.

1. **Concrete Crack Images for Classification (Corrupted)**
   - Intended for crack classification.
   - Usable images: 0. The dataset contained an invalid RAR / Mendeley JSON error payload.
2. **CICS**
   - 12,000 classification images (Crack vs Uncracked).
   - More than 6,185 exact MD5 duplicates were observed (>50%).
3. **DATA_Maguire_20180517_ALL**
   - 56,092 classification images of decks, walls, and pavements.
4. **Damage Detection Dataset for Concrete Structures with Multi-Feature Backgrounds**
   - 2,750 images with XML bounding boxes.
5. **MDMCS - A Benchmark Dataset for Multi-Damage Monitor**
   - 1,200 images with multi-damage segmentation annotations (crack, spalling, exposed rebar, corrosion).
6. **Reinforced Concrete Structure Segmentation Dataset**
   - 1,841 images with high-quality polygon annotations (Structural crack, Rebar corrosion, Microcrack, Minor spalling, Delamination, Moderate spalling, Structural deformation, Concrete crushing).

## 3. Dataset Sizes & 4. Annotation Types
| Dataset | Total Images | Annotation Type |
|---|---|---|
| Concrete Crack (Corrupted) | 0 usable | N/A |
| CICS | 12,000 | Image-level classification |
| DATA_Maguire_20180517_ALL | 56,092 | Image-level classification |
| Damage Detection | 2,750 | XML Bounding Box |
| MDMCS | 1,200 | JSON / PNG Mask |
| Reinforced Concrete | 1,841 | JSON Polygons |

## 5. Dataset Selection Rationale
**MDMCS** and the **Reinforced Concrete Structure Segmentation Dataset** were selected as the core training datasets because they directly provide high-quality pixel/polygon supervision required for semantic segmentation. 

## 6. Why Classification Datasets Were Not Used Directly for Segmentation
While classification datasets (CICS, DATA_Maguire) are useful for domain pretraining, they were excluded from the core segmentation training because image-level labels cannot provide the accurate, tight pixel boundaries needed to supervise semantic segmentation.

## 7. Why Bounding-Box Datasets Were Not Converted Into Fake Masks
The Damage Detection dataset (XML bounding boxes) was not used because directly converting bounding boxes into rectangular segmentation masks introduces noisy, artificial labels that destroy the true geometric boundary of the defects.

## 8. MDMCS Details
- 1,200 images with pixel-level segmentation.
- Official Split: Train = 1,000 | Validation = 100 | Test = 100
- Multi-class segmentation focusing on crack, spalling, exposed rebar, and corrosion.
- **Licensing Note**: MDMCS is used strictly under academic fair-use for research benchmarking purposes. It is currently flagged as `production_training_eligible = False` for commercial use.

## 9. Reinforced Concrete Segmentation Dataset Details
- 1,841 images with detailed JSON polygon annotations.
- Provided high-quality boundaries for various granular defects like Structural crack, Microcrack, Minor/Moderate spalling, Delamination, Concrete crushing, and Rebar corrosion. Polygons were successfully rasterized into pixel masks.

## 10. Dataset Normalization
The dataset normalization pipeline:
1. Converted source annotations (JSON polygons, distinct PNGs) into unified masks.
2. Resized images to **384x384**.
3. Resized masks to **384x384** using nearest-neighbor interpolation to preserve integer class IDs.
4. Validated polygons and removed empty shapes/corrupt files. 
Result: 3,041 normalized images and masks.

## 11. Label Mapping
The unified taxonomy mapping:
- `0 = Background`
- `1 = Crack` (from MDMCS crack, RC Structural crack/Microcrack)
- `2 = Spalling / Delamination` (from MDMCS spalling, RC Minor/Moderate spalling, Delamination, Concrete crushing)
- `3 = Corrosion / Exposed Rebar` (from MDMCS corrosion/exposed rebar, RC Rebar corrosion)
- `255 = Ignore`

## 12. Ignore-Label Handling
Structural deformation was mapped to **255 (IGNORE)**. It is outside the current three-defect taxonomy and should not be treated as negative/background evidence. It is excluded from loss and metric calculations.

## 13. Dataset Splits
**Normalized core segmentation dataset**: 3,041 images.
- **Train**: 2,472
- **Validation**: 284
- **Test**: 285

**CRITICAL DATA LEAKAGE LIMITATION**: The dataset splitting did not enforce strict building-level or site-level isolation. Because frames of the same physical structure or crack from slightly different angles could randomly appear in both the training and test sets, the reported test metrics (0.6734 mIoU) may be artificially inflated by data memorization. Generalization to entirely unseen buildings remains unproven.

**MDMCS official split**:
- Train = 1,000
- Validation = 100
- Test = 100

**Reinforced Concrete dataset**:
- Train = 1,472
- Validation = 184
- Test = 185

## 14. Class Distribution
**Class image presence:**
- Crack = 1,231 images / 40.5%
- Spalling = 1,410 images / 46.4%
- Corrosion = 1,275 images / 41.9%

**Pixel distribution:**
- Background = 79.82%
- Crack = 2.03%
- Spalling = 10.13%
- Corrosion = 8.02%

## 15. Pilot Experiment
A small pilot experiment (5 epochs) was executed in a CPU environment to validate the training pipeline, checkpoint generation, and metric calculation. It was not a model-quality result and metrics were excluded.

## 16. Full U-Net Experiment
- Architecture: U-Net (ResNet50)
- Training time: 5886.84 seconds
- Best validation epoch: 46
- Test Mean Defect IoU: 0.4464
- Test Mean Defect Dice: 0.6129

## 17. Full DeepLabV3+ Experiment
- Architecture: DeepLabV3+ (ResNet50)
- Training time: 2963.51 seconds
- Best validation epoch: 98
- Test Mean Defect IoU: 0.5811
- Test Mean Defect Dice: 0.7332

## 18. Research Ablation Experiments & 19. Complete Validation Ablation Table
| Experiment | Architecture | Backbone | Resolution | Loss | Val mIoU | Val Dice | Crack IoU | Spalling IoU | Corrosion IoU |
|---|---|---|---|---|---|---|---|---|---|
| Phase3_Baseline | DeepLabV3+ | ResNet50 | 384 | FocalDice | 0.5661970376968384 | 0.7190355658531189 | 0.6829206347465515 | 0.4699757397174835 | 0.5456947088241577 |
| Phase4_Res512 | DeepLabV3+ | ResNet50 | 512 | FocalDice | 0.5479847192764282 | 0.7065256834030151 | 0.6188573837280273 | 0.4930372536182403 | 0.532059371471405 |
| Phase5_LossCE | DeepLabV3+ | ResNet50 | 384 | CrossEntropy | 0.6151566505432129 | 0.7591085433959961 | 0.7077457904815674 | 0.525811493396759 | 0.6119126677513123 |
| Phase5_LossTversky | DeepLabV3+ | ResNet50 | 384 | TverskyFocal | 0.5601911544809805 | 0.7121661901473999 | 0.7134437561035156 | 0.4901449680328369 | 0.4769846200942993 |
| Phase5_LossWeightedCE | DeepLabV3+ | ResNet50 | 384 | WeightedCrossEntropyDice | 0.6109837293624878 | 0.7559818625450134 | 0.7147677540779114 | 0.548457682132721 | 0.5697256326675415 |
| Phase6_ArchUNet | U-Net | ResNet50 | 384 | FocalDice | 0.5448809862136841 | 0.7023696303367615 | 0.6484248042106628 | 0.5161473155021667 | 0.4700707793235779 |
| Phase6_ArchDeepLabEff | DeepLabV3+ | EfficientNet-B4 | 384 | FocalDice | 0.6256738901138306 | 0.7687327265739441 | 0.6851887702941895 | 0.5713486671447754 | 0.6204841136932373 |
| Phase6_ArchSegFormer | SegFormer | MiT-B3 | 384 | FocalDice | 0.5580520629882812 | 0.7162148356437683 | 0.5800498723983765 | 0.5504075884819031 | 0.543698787689209 |

## 20. Final Model Selection
**Selected model:** `Phase6_ArchDeepLabEff_best.pth`
- Architecture: DeepLabV3+
- Backbone: EfficientNet-B4
- Resolution: 384x384
- Loss: FocalDice
- Selection criterion: Validation Mean Defect IoU (The test set was NOT used for model selection).

## 21. Final Test Results
- Test images: 285
- Mean Defect IoU: 0.6734
- Mean Defect Dice: 0.8046
- Crack IoU: 0.7057
- Spalling IoU: 0.6540
- Corrosion IoU: 0.6604
*(Note: These are standard segmentation intersection-over-union/dice metrics, NOT pixel "accuracy")*

## 22. Error Analysis
- Checkpoint: Phase6_ArchDeepLabEff_best.pth
- Test images: 285

## 23. Small-defect Analysis
Performance degraded severely on smaller defect instances across all classes:
- Small Crack IoU = 0.45, Large Crack IoU = 0.95
- Small Spalling IoU = 0.48, Large Spalling IoU = 0.82
- Small Corrosion IoU = 0.29, Large Corrosion IoU = 0.76

## 24. Spalling/Corrosion Confusion
- Spalling → Corrosion = 467,694 pixels
- Corrosion → Spalling = 531,196 pixels
(Massive boundary ambiguity where concrete breaks to expose rebar).

## 25. Crack False Positives
- Crack FP ≈ 236k
- Crack FN ≈ 74k
(The model demonstrates heavy over-segmentation for cracks, confusing textures/joints for damage).

## 26. Limitations
- **Annotation bounds**: Semantic borders on spalling are inherently subjective, leading to hard upper limits on metric precision.
- **Small defect performance**: The model struggles to detect fine-grained, localized defects.
- **Domain shift**: Unknown performance on unseen real-world camera conditions/lighting.
- **No inherent scale**: Physical dimensions require scale/camera calibration.
- **Engineering safety**: Segmentation does not itself establish structural safety/severity. Need for engineering expert validation. Current results are benchmark/test-set segmentation results.

## 27. Reproducibility Information
- Random seeds were fixed where possible. All dataset preprocessing, training scripts, configs, ablation loops, error analysis, and metrics calculation are isolated in the exact scripts provided in the project history.
- The `INFERENCE` folder contains the precise exact load instructions to reproduce test inference.

## 28. Hardware/Environment
- The final experiment was trained using an **NVIDIA A100-PCIE-40GB** (~39.52 GB VRAM).
- Python/PyTorch versions were configured under a `gpu-pytorch` Conda environment.

## 29. Paper-Supported Claims
**Claims Supported by the Experiments:**
- EfficientNet-B4 DeepLabV3+ achieved the highest validation mIoU among the tested configurations.
- The final selected model achieved 67.34% mean defect IoU on the untouched test set.
- Small defects showed lower segmentation performance.
- Spalling and corrosion showed substantial inter-class confusion.
- Crack predictions exhibited substantial false-positive over-segmentation.

## 30. Claims NOT Supported
- Real-world structural safety
- Engineering severity accuracy
- Universal generalization
- Production-level accuracy
- Clinical-style sensitivity
- Certified structural inspection
- Perfect defect detection
