# Phase 9.5: CivilCortex Data Consistency & Public Dataset Utilization Audit v0.1

## 1. Executive Summary
This document confirms the internal consistency of the Phase 9 field data specifications with the existing CivilCortex backend architecture. The repository's identity models properly support longitudinal defect tracking, and public dataset utilization rules have been established to strictly isolate unverified, research-only data from production-domain field data.

**STATUS: READY FOR CONTROLLED PUBLIC-DATA BASELINES + FIELD COLLECTION**

## 2. Current System & Data State
The repository contains robust database models (`Building`, `Floor`, `Area`, `StructuralElement`, `Crack`, `CrackObservation`, `InspectionImage`) mapped perfectly to the CivilCortex identity hierarchy. The existing `metadata_schema.py` and `api_models.py` successfully represent CV contracts (`CVAnalysisResult`, `CVDetection`, `CVMeasurement`).

## 3. Phase 9 Consistency Findings
**Finding:** A schema gap existed where `metadata_schema.py::ImageMetadata` lacked `floor_id`, `area_id`, `structural_element_id`, and `observation_id`, which were present in the Phase 9 `field_collection_schema.json` and the backend models.
**Action Taken:** `metadata_schema.py` was directly updated to include these missing attributes, closing the schema gap.

## 4. Identity Hierarchy Audit
The system flawlessly supports the conceptual identity requirement:
- `Crack` (`cracks` table) = persistent physical entity (`defect_instance_id`).
- `CrackObservation` (`crack_observations` table) = visit-specific observation of the defect.
- `InspectionImage` (`inspection_images` table) = photographic evidence.

The backend does NOT conflate images with physical cracks. Multiple images belonging to the same observation correctly map to the same `crack_id` and `observation_id`.

## 5. CV Contract Audit
The `CVAnalysisResult` and `CVDetection` models properly decouple primary `defect_type` (Crack, Spalling, Efflorescence) from `morphology_tags` (horizontal, vertical, diagonal, branching, irregular) as an array of attributes. This prevents morphology from acting as a mutually exclusive class, which aligns completely with Phase 9 SOP. "No defect" correctly remains an image-level state (`image_status: NO_DEFECT`).

## 6. Calibration / Measurement Audit
The `CVMeasurement` contract enforceably distinguishes `PIXEL_ONLY`, `PHYSICAL_CALIBRATED`, `PHYSICAL_ESTIMATED`, and `UNAVAILABLE`.
The pydantic validation (`validate_calibration_rules`) explicitly rejects physical dimension assignment if the `calibration_status` is `PIXEL_ONLY` or `UNAVAILABLE`. It also enforces the presence of a `calibration_reference` when marked as calibrated.

## 7. Annotation Consistency Audit
The `annotation_validator.py` explicitly validates polygon bounds and self-intersections. It enforces standard `defect_type` and `morphology_labels`. The validation logic perfectly aligns with the Phase 9 SOP emphasizing tight segmentation and avoiding hidden geometry hallucination.

## 8. Field Data Target Audit
The targets across `field_dataset_target_matrix.json`, `.md`, and specifications are mathematically consistent:
- **Minimum Gate:** 10 sites, 2,000 physical defect instances.
- **Recommended:** 20 sites, 3,500 physical defect instances, 15,000 images.
- **Defect Distribution:** Crack (40% / 1500 min), Spalling (20% / 800 min), Efflorescence (20% / 800 min), Hard Negative (20% / 800 min). Note: the percentages are guidelines but absolute minimum instance counts must be met.
- **Morphology:** 20% representation each for horizontal, vertical, diagonal, branching, irregular. (Recognized as non-mutually exclusive attributes).

## 9. Public Dataset Audit Table
*Source images only (excludes 1,300 PNG segmentation masks/overlays incorrectly evaluated in raw Phase 8).*

| Dataset | Source Images | Annotation | Classification | Bounding Boxes | Masks | Defect Classes | Morphology | Calibration | Structure ID | Longitudinal | Hard Negatives | License Status | Potential Use | Training Eligibility | Blocking Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SDNET2018** | 56,092 | Classification | Yes | No | No | Crack | No | No | Bridge ID | No | Yes | UNVERIFIED | Research/Baseline | **BLOCKED** | Unverified exact dataset license |
| **CCIC** | 40,000 | Classification | Yes | No | No | Crack | No | No | None | No | Yes | CC-BY 4.0 | Pretraining | ELIGIBLE | N/A |
| **RC1841** | 1,841 | Mask | Yes | No | Yes | Crack | No | No | None | No | Minimal | UNVERIFIED | Research/Baseline | **BLOCKED** | Unverified exact dataset license |
| **DAMAGE_DETECTION** | 2,750 | BBox | Yes | Yes | No | Crack | No | No | None | No | Yes | UNVERIFIED | Research/Baseline | **BLOCKED** | Unverified exact dataset license |
| **MDMCS** | 1,200 | Mask | Yes | No | Yes | Crack | No | No | None | No | Minimal | UNVERIFIED | Research/Baseline | **BLOCKED** | Unverified exact dataset license |
| **CICS** | 12,000 | Classification | Yes | No | No | Crack | No | No | None | No | Minimal | UNVERIFIED | Research/Baseline | **BLOCKED** | Unverified exact dataset license |

*(Original Source-Image Exact Duplicates: 8,464 within-dataset, 651 cross-dataset)*

## 10. Public Dataset Licensing Status
Only **CCIC** has a verified dataset-level license declaration (CC-BY 4.0 via Mendeley). The others rely on default repository/platform assumptions. As per CivilCortex governance, unverified dataset licenses are explicitly blocked from production training to avoid commercial IP liability.

## 11. Public Dataset Utilization Matrix
| Dataset | License | Spatial Supervision | Primary Use | Production Training? | Research Use? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SDNET2018** | UNVERIFIED | None | Baseline Classification | **NO** | YES |
| **CCIC** | CC-BY 4.0 | None | Feature Pretraining | YES | YES |
| **RC1841** | UNVERIFIED | Semantic Masks | Baseline Segmentation | **NO** | YES |
| **DAMAGE_DETECTION**| UNVERIFIED | Bounding Boxes | Baseline Detection | **NO** | YES |
| **MDMCS** | UNVERIFIED | Semantic Masks | Baseline Segmentation | **NO** | YES |
| **CICS** | UNVERIFIED | None | Exclusion (High overlap) | **NO** | NO |

## 12. Data Leakage Audit
The `split_generator.py` explicitly supports group-aware splitting for SDNET2018 (by Bridge ID). For unstructured public datasets, deterministic `pHash` clusters are used to purge overlaps. 
For Track B (Field Data), the final CivilCortex test set must consist strictly of genuinely unseen buildings (structure-level split), isolated entirely from public data.

## 13. Demo-Pipeline Isolation Audit
The current inference pipeline is correctly isolated. `CVAnalysisResult` statically assigns `model_version: str = "PIPELINE_DEMO_ONLY"`. These results populate the `observations` UI dynamically without persisting into the training metadata schemas. 

## 14. Blockers
- None related to data consistency.
- Production readiness is still blocked pending field data collection (see Phase 9 Schema Gate).

## 15. Non-Blockers
- Public datasets lack structure IDs (non-blocking for *research* track usage, as long as they are barred from the field test set).
- Calibration absence in public datasets (non-blocking for pretraining weights).

## 16. Required Actions
- Maintain strict conceptual and operational separation between Track A (Public Data) and Track B (Field Data).
- Treat Track B as the only path to closing the Production Readiness Gate.

## 17. Recommended Next Phase
PHASE 10: Track A (Public Data) Controlled Baseline Experimentation OR Track B (Field Data) Acquisition initiation.

## 18. Explicit Readiness Decision
**READY FOR CONTROLLED PUBLIC-DATA BASELINES + FIELD COLLECTION**
