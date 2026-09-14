# Phase 10D: Field Data Acquisition, Annotation & Dataset Engineering Plan v0.1

## 1. Purpose
This document establishes the formal, reproducible protocol for acquiring, validating, and annotating the CivilCortex field dataset. It dictates rigorous academic and engineering standards, preventing data leakage, and ensuring that future ML experiments are based on transparent, limitation-aware, and reproducible methods rather than optimized benchmarks.

## 2. Source-of-Truth Target Reconciliation
- **Contradiction:** The previous mathematical contradiction between 2,000 total instances and 3,100 class-specific targets is formally **RESOLVED**.
- **Status:** **APPROVED**. Engineering Leadership has approved **Option B**. 
- **Target Matrix:**
  - **≥3,100** unique physical defect instances total.
  - **≥1,500** crack instances.
  - **≥800** spalling instances.
  - **≥800** efflorescence instances.
  - **≥800** hard negative instances (tracked separately, NOT included in the 3,100 defect instances).

## 3. Mandatory Sequence of Execution
Field collection may now commence based on the approved targets. The strictly enforced sequence is:
1. Target decision (COMPLETED/APPROVED)
2. Approved collection matrix (COMPLETED)
3. Field acquisition
4. Annotation
5. Peer review / QC
6. Readiness gate
7. Controlled field experiments

## 4. Field Collection Strategy
Data is collected in adherence to the established hierarchy (`source` -> `site` -> `building` -> `floor` -> `area` -> `structural_element` -> `inspection` -> `observation` -> `image` -> `defect_instance`). All captures must preserve this provenance. 

## 5. Site/Building Sampling Strategy
Convenience sampling is prohibited without explicit acknowledgment. The sampling must deliberately track and balance structural element diversity, material composition, lighting constraints, and hardware permutations. **Crucially, sampling protocols must not be altered merely to optimize future model performance.**

## 6. Image Capture Protocol
Images must be collected immutably.
`Raw field image → source storage → SHA-256 → perceptual hash → metadata validation → privacy review → quality review → dataset registration → annotation`.
Images must not be modified to make them pass validation.

## 7. Privacy and Safety
Field images undergo an explicit privacy review resulting in one of three states: `REJECT`, `REDACT`, or `ACCEPT`. Any image containing PII, faces, license plates, or sensitive documents must be redacted or rejected. Ethics/consent approvals must be documented.

## 8. Annotation Workflow
1. Image quality review.
2. Defect identification and classification (crack, spalling, efflorescence).
3. Physical instance separation.
4. Tight polygon/mask annotation.
5. Deterministic morphology extraction.
6. Calibration linkage.
7. Annotation review.

## 9. Physical Defect Identity
**ONE PHYSICAL DEFECT = ONE PERSISTENT DEFECT INSTANCE**.
Multiple images across varying viewpoints or temporal inspections are *observations* of the same physical defect instance. Automated pipelines will not spontaneously mint new physical identities; this is governed by contextual matching (`CANDIDATE` -> `MONITORED` -> `REPAIRED`).

## 10. Morphology Annotation
Morphology (horizontal, branching, etc.) is a structured attribute layer, not a ground truth class. UNKNOWN / UNCERTAIN are permitted where visual evidence is insufficient. Morphology is never fabricated.

## 11. Calibration Protocol
Calibration enforces the following states: `PIXEL_ONLY`, `PHYSICAL_CALIBRATED`, `ESTIMATED`, `UNAVAILABLE`. Physical geometry and width measurements require explicit, validated coplanar references. Uncalibrated observations strictly yield pixel measurements.

## 12. Hard Negatives
A deliberate non-defect population (e.g., joints, seams, shadows, surface textures) must be collected and labeled explicitly as hard negatives. They must not be conflated with physical defect instances.

## 13. Longitudinal Collection
Observations of the same defect over time must be explicitly tracked using the `defect_instance_id`. Fake sequences or unrelated images used as false repeated observations are strictly prohibited.

## 14. Quality Control
Automated systems will run `field_ingestion_validator.py` to enforce hierarchy, calibration, duplicate hashing, and geometry validity without mutating original data. 

## 15. Reviewer/Adjudication Workflow
At least 20% of annotations will undergo peer review. Disagreements will trigger an adjudication workflow, preserving version history. Academic-grade inter-annotator agreement metrics (IoU, Cohen's kappa) will be derived post-annotation.

## 16. Dataset Schema
Schema explicitly dictates referential integrity. Incompatible hierarchies (e.g., Image 1 assigned to Defect A on Wall X, but later redefined to Wall Y) will be explicitly flagged and rejected by the validator.

## 17. Manifest/Versioning
A manifest (`field_manifest_schema.json`) enforces checksums, hashing, versioning, and privacy state tracking. This ensures the exact reconstruction of training assets for publication reproducibility.

## 18. Split Strategy
Splits will be frozen prior to model development. 
- Generalization Test Set: Unseen buildings/sites.
- Longitudinal Test Set: Exact physical defect sequences.
- Validation: Prevents same-defect leakage.
- Hard Negative / Calibration Test Sets.

## 19. Readiness Gates
Currently **BLOCKED**. Zero real qualifying field instances exist. Test fixtures, synthetics, and public pretraining data cannot bypass the production gate. Production training is blocked until 3,100 qualifying instances are acquired.

## 20. Collection Risks & Limitations
Explicit dataset limitations (e.g., rare defect underrepresentation, sensor bias, geometric occlusions) will be formally documented rather than suppressed for publication strength.

## 21. Phase 10E Handoff
Upon successful completion of the readiness gates and actual field data collection, Phase 10E will commence with Controlled Field-Data Experiments and rigorous Statistical Evaluation (including confidence intervals and meaningful group stratification). Phase 10E is entirely contingent on the acquisition of the approved 3,100 target.
