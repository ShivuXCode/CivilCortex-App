# CivilCortex Field Annotation SOP v0.1

## 1. Overview
This Standard Operating Procedure strictly dictates the process for converting raw field photographs into ML-ready ground-truth annotations.

## 2. Step-by-Step Annotation Process

**STEP 1: Image Quality Assessment**
Reject unusable images (blurry, completely dark, obscured).

**STEP 2: Defect Type Identification**
Select primary category: Crack, Spalling, Efflorescence, Hard Negative, Normal, or Uncertain.

**STEP 3: Content Verification**
Ensure the defect is visibly present and matches the metadata context.

**STEP 4: Spatial Annotation**
Create tight spatial annotations (Masks or Polygons). Do NOT hallucinate hidden geometry behind occlusions. Annotate visible evidence only.

**STEP 5: Morphology Attributes**
For cracks, assign multi-label attributes: `horizontal`, `vertical`, `diagonal`, `branching`, `irregular`. Do not force a crack into a single category if multiple apply.

**STEP 6: Occlusion Recording**
Mark areas of the defect obscured by pipes, cables, or shadows.

**STEP 7: Calibration State**
Record whether a valid calibration target is present and coplanar in the image.

**STEP 8: Measurement Information**
Extract `pixels_per_mm` ONLY if step 7 is valid.

**STEP 9: Defect Identity Linking**
Ensure the annotation explicitly links to the `defect_instance_id` to unify multiple images of the same crack.

**STEP 10: Review**
Submit for peer review.

## 3. Quality Control & Escalation
- **Target:** Minimum 20% peer-review coverage.
- **Tracking:** Track inter-annotator disagreement, rejected/corrected annotations.
- **Escalation:** Difficult engineering cases must be escalated to a qualified structural engineering reviewer. The ML annotator is NOT responsible for declaring structural safety.
