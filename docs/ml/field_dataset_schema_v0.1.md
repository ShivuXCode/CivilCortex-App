# CivilCortex Model Development Readiness Gate

## OVERVIEW
The ML engineering team MUST NOT proceed to architecture selection, hyperparameter tuning, or model training until the real field dataset satisfies every check in this formal gate.

## [ ] DATA VOLUME
- [ ] Minimum 2,000 unique physical defect instances collected and annotated.

## [ ] CLASS COVERAGE
- [ ] Minimum 1,500 crack instances.
- [ ] Minimum 800 spalling instances.
- [ ] Minimum 800 efflorescence instances.
- [ ] Minimum 800 labeled hard negatives (construction joints, formwork marks, stains).

## [ ] MORPHOLOGY
- [ ] Explicit ground-truth morphology tags applied (Horizontal, Vertical, Diagonal, Branching, Irregular).

## [ ] SPATIAL ANNOTATION
- [ ] All defects labeled with validated instance-level masks or polygons (bounding boxes alone are insufficient).

## [ ] CALIBRATION
- [ ] At least 40% of the dataset includes a validated, coplanar physical scale reference for measurement validation.

## [ ] DIVERSITY
- [ ] Minimum 10 distinct sites/structures.
- [ ] Element diversity (Beams, Columns, Slabs, Walls, Masonry).
- [ ] Lighting diversity (Daylight, Artificial, Low Light).
- [ ] Minimum 3 distinct camera hardware configurations.

## [ ] LEAKAGE CONTROL
- [ ] Train/Val/Test splits enforce strict building-level and defect-identity isolation.
- [ ] Duplicate control executed and zero-leakage verified.

## [ ] LONGITUDINAL DATA
- [ ] Contains repeated observations of real physical defects over time, properly linked by `defect_instance_id`.

## [ ] LICENSE / CONSENT
- [ ] Production-use rights explicitly secured for all field captures.
- [ ] Documented field-site permissions.

## [ ] QUALITY CONTROL
- [ ] Minimum 20% peer-review annotation coverage.
- [ ] Disagreements documented and escalated appropriately.

## [ ] PRIVACY & SAFETY
- [ ] PII successfully redacted from the ML pipeline.
- [ ] Safety protocols followed during collection.
