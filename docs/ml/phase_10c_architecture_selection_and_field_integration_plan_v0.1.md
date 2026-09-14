# Phase 10C: Architecture Selection and Field Integration Plan v0.1

## 1. Executive Summary
Phase 10C establishes the formal architectural requirements, provisional CV architecture decisions, and the field-data integration strategy for the CivilCortex production model. This plan dictates the strict separation between visual defect detection and persistent physical identity tracking, decoupling the CV pipeline from the structural engineering and risk assessment layers. Mask R-CNN is designated as the primary provisional instance-segmentation candidate pending field validation. Finally, an unresolved mathematical contradiction regarding field-data targets remains explicitly blocked prior to production training.

## 2. Evidence Base
The architectural decisions herein are formulated from:
- `docs/ml/phase_10b_public_dataset_baseline_results_v0.1.md`
- `docs/ml/phase_9_5_data_consistency_and_public_dataset_utilization_audit_v0.1.md`
- `docs/ml/field_data_collection_protocol_v0.1.md`
- `docs/ml/field_dataset_target_matrix_v0.1.md`
- `docs/ml/field_dataset_schema_v0.1.md`
- `ml_pipeline/dataset/metadata_schema.py`
- Phase 10B execution logs verifying the public dataset baseline adapter structures.

## 3. Current Data Reality

### A. What Public Datasets Provide
- SDNET2018: Image-level classification.
- RC1841: Mask/polygon-level segmentation.
- DAMAGE_DETECTION_2750: Bounding box detection.
- **Missing:** Validated spatial spalling/efflorescence data, explicit thin-crack width-bands, ground-truth morphology, coplanar calibration references, longitudinal structural identity tracking, and guaranteed production licensing (except CCIC).

### B. What the Field Dataset is Designed to Provide
- Multi-class instance-level polygons (Cracks, Spalling, Efflorescence).
- Labeled hard negatives.
- Identity hierarchy (building, area, structural element).
- Morphological descriptors (horizontal, branching, etc.).
- Explicit calibration markers.
- Longitudinal multi-observation sequences.

### C. What CivilCortex Ultimately Requires
- Precise geometric measurement of persistent, distinct physical crack instances across repeated observation sessions.
- Reliable separation of multiple distinct defects on the same structural element.

## 4. CivilCortex CV Requirements
- **Defect Taxonomy:** Crack, Spalling, Efflorescence.
- **Spatial Output:** Instance-specific masks mapped to polygons, facilitating precise geometry and morphology extraction.
- **Thin-Defect Behavior:** Recall and boundary quality on hairline cracks without artificial dilation.
- **Measurement:** Physical measurements require explicit validated calibration evidence.
- **Longitudinal Monitoring:** Persistent defect tracking across sequential visits.
- **Separation of Concerns:** The CV network predicts visible evidence; it does NOT predict structural risk, severity, or repair plans.

## 5. Candidate Architecture Families
- **Instance Segmentation (Primary Candidate):** Identifies distinct defect instances and provides spatial masks/boxes.
- **Semantic Segmentation + Deterministic Separation (Alternative):** A single pixel-mask per class separated into instances using geometry, skeletonization, or topology-aware processing.
- **Detection-Only (Baseline):** Limited applicability due to bounding box inability to capture crack morphology or true physical width.
- **Promptable Segmentation (Research):** SAM or equivalent for annotation assistance but limited by inference constraints.

## 6. Architecture Decision Matrix

| Candidate Family | Purpose | Input | Output | Annotation Requirements | Suitability for CivilCortex | Recommendation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Mask R-CNN (Instance Segmentation)** | Delineate independent physical defect evidence. | RGB Image | BBoxes + Instance Masks + Classes | Polygon / Mask Instances | Natively outputs distinct geometries required for morphology and longitudinal tracking. Thin-crack recall needs field validation. | **PRIMARY PROVISIONAL CANDIDATE** |
| **Semantic Segmentation + Separation** | Pixel-level mask generation. | RGB Image | Class Pixel Masks | Semantic Masks | Fails to separate intersecting or nearby cracks natively; heavily reliant on deterministic post-processing. | **ALTERNATIVE / FALLBACK** |
| **Detection-Only** | Localization. | RGB Image | BBoxes | Bounding Boxes | Insufficient. Cannot capture crack width, orientation, or morphology accurately. | **REJECTED (Baseline Only)** |
| **Promptable Segmentation (SAM)** | Automated labeling. | RGB Image + Point/Box Prompt | Instance Masks | Zero-shot | Too heavy for rapid field inference; useful only as an offline annotation accelerator. | **RESEARCH / ANNOTATION ONLY** |

## 7. Provisional Architecture Recommendation
**Primary Provisional Candidate:** Mask R-CNN or equivalent instance-segmentation architecture.

*This selection remains provisional. The final production candidate requires field-data experiments proving adequate thin-crack recall, boundary quality, and computational feasibility under field deployment constraints.*

## 8. Production CV Pipeline Conceptual Flow
The production flow is explicitly decoupled from engineering assessment. The neural network provides pure visual evidence.

1. **Image Ingestion:** Capture arbitrary field images.
2. **Quality / Privacy Check:** Assess illumination, focus, blur, and redact PII.
3. **Detection / Segmentation:** Provisional Mask R-CNN detects *Candidate Visual Defect Instances* (Bounding box + Mask + Defect Type).
4. **Geometry / Morphology Extraction:** Deterministic processing extracts valid orientation, shape, and visible extent from the mask. Morphology tags (e.g., branching, horizontal) are extracted deterministically.
5. **Calibration Validation:** Verify valid coplanar scale references.
6. **Measurement:** Produces pixel measurements (default) or physical measurements (only if calibration is validated).
7. **Identity Workflow / Contextual Matching:** Matches visual candidates against previous records.
8. **Structured CV Observation:** Generates standardized JSON output.
9. **Engineering Assessment Layer (External):** Combines structured CV observation with structural context and history.
10. **Risk / Recommendation Layer (External):** Evaluates structural risk and outputs recommendations.
11. **LLM Synthesis (External):** Explanation and narrative generation only.

## 9. Field Data Integration Pipeline
The pipeline ensures that field captures maintain their relational integrity.

`Field Capture → Source Metadata → Site/Building Hierarchy → Inspection → Observation → Image → Annotation → Calibration → Validation → Quality Control → Deduplication → Group-Aware Split → Dataset Manifest → Training → Model Registry.`

**Identity Mapping Rule:** 
**ONE PHYSICAL DEFECT = ONE PERSISTENT DEFECT INSTANCE**
A model prediction is merely a visual observation. It must pass through contextual identity matching to link to a `defect_instance_id`. Repeated observations/photographs of a defect are observations, not new defects.

## 10. Dataset Manifest Strategy
Production experiments require strict provenance tracing. Every sample in a training manifest must be resolvable to its source, site, building, inspection, observation, image, defect instance, annotation version, and calibration record.

## 11. Split/Leakage Strategy
Splitting must occur before processing. The evaluation regimes are:
- **Structure-Level Generalization (Test Set):** Complete isolation. Test sites/structures must be unseen in training.
- **Standard Validation:** May use training sites, but must strictly prevent the same physical defect from appearing in train and val.
- **Longitudinal Evaluation:** Dedicated subset holding out complete multi-observation sequences of physical defects. Within any individual experiment, all observations belonging to the same physical defect must remain in the same split. No physical defect may have its observations distributed across train/validation/test.
- **Hard-Negative / Calibration Evaluation:** Dedicated evaluation subsets for precise testing.

## 12. Evaluation Framework
Single "accuracy" metrics are rejected. The evaluation matrix includes:
- **Segmentation:** Mask Precision, Mask Recall, F1/Dice, IoU.
- **Detection:** Bounding Box mAP.
- **Classification:** Precision, Recall, Confusion Matrix.
- **Measurement:** Mean Absolute Error (MAE), Relative Error, Uncertainty bands.
- **Calibration:** Accuracy against controlled reference states.
- **Longitudinal Matching:** Matching Precision/Recall, False New/Existing rates.
- **Hard Negatives:** False Positive Rate on formwork marks, stains, and shadows.

## 13. Thin-Crack Evaluation
Thin cracks must be evaluated across width-bands using mask precision and mask recall. General bounding-box mAP is irrelevant for thin-crack validation. Ground truth annotations MUST NOT artificially dilate thin cracks. Physical width accuracy cannot be claimed solely from large-crack segmentation performance.

## 14. Calibration and Measurement Architecture
Calibration follows existing metadata states:
- `PIXEL_ONLY` (Default)
- `PHYSICAL_CALIBRATED`
- `ESTIMATED`
- `UNAVAILABLE`

**Flow:** Pixel Geometry → Calibration Validation → Valid Coplanar Reference? 
- NO → `PIXEL_ONLY`
- YES → `PHYSICAL_CALIBRATED` + Measurement Uncertainty.
Model confidence is entirely distinct from calibration validity, measurement uncertainty, and engineering risk.

## 15. Longitudinal Monitoring Architecture
Visual candidates must pass through contextual matching.
**Flow:** CV Candidate → Candidate Existing Defect(s) → Contextual Evidence → User/Authorized Confirmation (when uncertain) → Existing Defect OR New Defect.

Matches utilize geometry, orientation, site, floor, and prior observations. Weak matches are never forced automatically.
**State Machine Preserved:**
- `CANDIDATE` → `MONITORED` → `DISMISSED`
- `MONITORED` → `REPAIRED`
- `REPAIRED` → `MONITORED`

## 16. Public + Field Data Strategy
Field data operates as the dominant production asset. 
- **CCIC:** Controlled pretraining baseline due to CC-BY 4.0 license.
- **SDNET, RC1841, DAMAGE_DETECTION_2750, MDMCS:** Research and baseline sources only.
- **CICS:** Excluded due to SDNET overlap.
Unverified public dataset licenses exclude those datasets from production domain-adaptation strategies.

## 17. Model Versioning / Experiment Reproducibility
Minimal reproducible tracking will capture: dataset version, manifest hash, code commit, architecture configuration, pretrained weights source, hyperparameters, random seed, training device, and split definition.

## 18. Production Readiness Gates
**STATUS: BLOCKED**
A mathematical contradiction exists in the Phase 9 field data documentation.
- **Total Minimum Target:** 2,000 unique physical defect instances.
- **Class Coverages:** Minimum 1,500 cracks, 800 spalling, 800 efflorescence. The subtotal of physical defect instances is 3,100 (excluding 800 hard negatives, which are a separate population).

This contradiction (2,000 total vs. 3,100 physical instances) must be explicitly resolved by engineering leadership before the field-data gate can be considered satisfied and production training can commence.

## 19. Risks and Open Questions
1. Mask R-CNN latency under field hardware constraints.
2. The resolution of the field dataset mathematical contradictions.
3. Establishing field morphology validity without overfitting to labeling bias.

## 20. Phase 10D Handoff
Phase 10C is complete pending resolution of the data gate target contradiction. Phase 10D will proceed to actual architecture implementation upon receipt of sufficient field data that satisfies the clarified readiness gates.
