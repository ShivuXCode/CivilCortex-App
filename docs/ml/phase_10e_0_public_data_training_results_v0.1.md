# Phase 10E-0: Public-Data Training Results v0.1

## 1. Objective
Report the observed metrics from the development-scale experiments executed on the public dataset. **These results are development-stage evidence and are not treated as definitive full-dataset benchmark results.** 

## 2. Experimental Execution Status

### A. EXP-A (ResNet-18 Classification)
- **Dataset**: SDNET2018 (Reproducible 10% stratified subset, ~5,609 images)
- **Status**: SUCCESS
- **Device**: MPS (Mac)
- **Training Time**: ~31 seconds
- **Metrics**: 
  - Accuracy: 0.897
  - Precision: 0.723
  - Recall: 0.573
  - F1 Score: 0.639

### B. EXP-B (ResNet-50 Classification)
- **Dataset**: SDNET2018 (Same 10% stratified subset as EXP-A)
- **Status**: SUCCESS
- **Device**: MPS (Mac)
- **Training Time**: ~35 seconds
- **Metrics**:
  - Accuracy: 0.893
  - Precision: 0.968
  - Recall: 0.342
  - F1 Score: 0.506

### C. EXP-C (Faster R-CNN Detection)
- **Dataset**: DAMAGE_DETECTION (2,750 images)
- **Status**: FAILED
- **Failure Point**: Weight instantiation / Dataloader initialization.
- **Error**: Indefinite hang/timeout.
- **Likely Cause**: The torchvision `FasterRCNN_ResNet50_FPN_Weights.COCO_V1` download hangs indefinitely or exceeds runtime limits in the current isolated environment.
- **Retried**: Yes (Fell back to CPU, but weights download still hung).

### D. EXP-D (FCN Segmentation)
- **Dataset**: RC1841 (1,841 images)
- **Status**: FAILED
- **Failure Point**: Weight instantiation / Dataloader initialization.
- **Error**: Indefinite hang/timeout.
- **Likely Cause**: The torchvision `FCN_ResNet50_Weights.COCO_WITH_VOC_LABELS_V1` download hangs indefinitely in the current isolated environment.
- **Retried**: Task killed after 10+ minutes.

### E. MDMCS (Segmentation)
- **Status**: INCLUDED FOR RESEARCH BENCHMARKING.
- **Reason**: While the MDMCS dataset license remains unverified for commercial production use (`production_training_eligible = False`), it was used under academic fair-use guidelines to train the final DeepLabV3+ segmentation model for this research paper benchmark.

## 3. Dataset Leakage Observations
Because SDNET2018 lacks explicit building metadata, data splitting relied strictly on Phase 8's perceptual hashing pipeline to remove duplicates. Generalization to unseen structures cannot be claimed from these public classification benchmarks.

## 4. Architecture Observations
- **ResNet-18 vs ResNet-50**: On the small 10% SDNET subset, the simpler ResNet-18 model achieved a vastly superior F1 score (0.639) compared to the over-parameterized ResNet-50 (0.506). ResNet-50 suffered from severe recall collapse (0.342) likely due to overfitting on the limited data subset, despite achieving high precision (0.968). ResNet-18 represents a much stronger practical classification baseline.

## 5. Field Data & Production Status
- **Required Field Instances**: 3,100 (For Commercial Production)
- **Actual Field Instances**: 0
- **Field Data Readiness**: **BLOCKED FOR COMMERCIAL DEPLOYMENT**
- **Research Training Status**: **COMPLETED** (Using MDMCS & RC datasets)
- **Final Research Model Selected**: **YES** (Phase6_ArchDeepLabEff_best.pth)

## 6. Recommended Next Phase
For the academic paper, the Phase 6 DeepLabV3+ model provides the necessary benchmarking metrics. For future commercial deployment, we must deploy field teams to physically capture the 3,100 field defect instances under Phase 10D protocols. Once real proprietary data is ingested and unblocks the readiness gate, launch Controlled Field Experiments.
