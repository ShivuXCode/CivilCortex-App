# CivilCortex Model Selection Requirements v0.1

## Overview
Model architecture selection must be driven by dataset characteristics and the rigorous output contract (`CVAnalysisResult`), rather than picking a familiar architecture like YOLOv8 purely out of convenience. 

## 1. Required Capabilities
The selected model family must natively support or be adaptable to the following:
- **Instance Segmentation:** Bounding boxes are insufficient for morphological analysis (branching, diagonal extent) of cracks. The model must produce a spatial mask (`CVGeometry`).
- **Thin/Small Object Detection:** Concrete cracks are frequently only a few pixels wide. Architectures heavily reliant on aggressive downsampling (e.g., standard YOLO grid cells) risk losing spatial evidence of thin defects.
- **Multiclass Support:** Must distinguish between Crack, Spalling, and Efflorescence.

## 2. Architecture Candidates Evaluation
| Architecture Family | Segmentation Quality | Thin Defect Handling | Latency (Inference) | Annotation Requirements |
| :--- | :--- | :--- | :--- | :--- |
| **Mask R-CNN** | High (Instance-level) | Medium (Dependent on RoI Align resolution) | High | Instance masks required |
| **YOLO-Seg (v8/v11)** | Medium | Low (Aggressive downsampling risks thin cracks) | Low | Instance masks required |
| **U-Net / DeepCrack** | High (Semantic-level) | High (Preserves spatial resolution well) | Medium | Semantic masks required |
| **SAM 2 / Foundation** | Very High | High | Very High | Minimal (Zero-shot / Prompts) |

## 3. Dataset Constraints on Selection
Based on the Phase 8 audit:
1. **Lack of Multi-class Masks:** The public datasets (RC1841, MDMCS) primarily contain **Crack-only** masks. Training an Instance Segmentation model for Spalling/Efflorescence is currently **blocked** by a lack of spatial annotations.
2. **Bounding Box Datasets:** The DamageDetection dataset provides only bounding boxes. This cannot be natively merged with Mask R-CNN training without pseudo-labeling.

## 4. Production Constraints
The production model must emit:
1. `defect_type` (classification)
2. `confidence`
3. `mask` (for morphology analysis)

## 5. Recommendation
Do not select a final architecture yet. The current dataset heavily favors **Semantic Segmentation** (like U-Net) for cracks due to the nature of the RC1841/MDMCS datasets, but the production contract requires **Instance Level** reporting. True model selection is blocked until field data for Spalling and Efflorescence instances with spatial masks is acquired.
