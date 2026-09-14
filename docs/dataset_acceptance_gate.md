# CivilCortex Dataset Acceptance Gate

## 1. Objective
Model training MUST remain blocked until every criterion in this acceptance gate is satisfied. This ensures that the dataset is legally usable, scientifically valid, free of leakage, and structurally diverse.

## 2. Gate Checklist

- [ ] **Licenses Verified:** All dataset licenses and usage rights explicitly verified.
- [ ] **Provenance Maintained:** Public dataset provenance and original attribution preserved.
- [ ] **Commercial Clearance:** No unresolved commercial-use restrictions in the production training data.
- [ ] **Data Integrity:** No corrupt images in the final manifest.
- [ ] **Privacy Clearance:** No unacceptable PII (faces, license plates, etc.) present.
- [ ] **Exact Duplicates Removed:** Cryptographic hash (SHA-256) confirms 0 exact duplicates.
- [ ] **Near-Duplicates Grouped:** Perceptual duplicates grouped by session/site to prevent leakage.
- [ ] **Instance Tracking:** Physical defect instances correctly identified and tracked across images.
- [ ] **Geometric Validity:** Polygon geometry validated (no self-intersections, no out-of-bounds coordinates).
- [ ] **Taxonomy Validation:** Defect taxonomy strictly matches `crack`, `spalling`, or `efflorescence`.
- [ ] **Morphology Validation:** Morphology tags correctly validated as attributes (not separate masks).
- [ ] **Hierarchy Populated:** Building/site/session grouping metadata populated where available.
- [ ] **Split Generation:** Group-aware Train/Validation/Test split generated.
- [ ] **Leakage Audit:** Explicit check confirms NO building/site leakage into the held-out Test set.
- [ ] **Site Diversity:** Minimum site diversity (≥ 10 sites) achieved.
- [ ] **Instance Diversity:** Minimum physical defect-instance diversity (≥ 2,000 instances) achieved.
- [ ] **Negative Coverage:** Negative/hard-negative imagery adequately represented.
- [ ] **Camera Diversity:** Captured across ≥ 3 genuinely different sensor configurations.
- [ ] **Measurement Subset:** Measurement-validation subset (Tier B) isolated and properly calibrated.
- [ ] **Ground Truth:** Measurement ground truth strictly recorded for Tier B.
- [ ] **Quality Report:** Formal dataset quality report JSON generated.
- [ ] **Split Manifest:** Final dataset split manifest generated.
- [ ] **Version Freeze:** Dataset version semantically frozen (e.g., `v0.1`).

## 3. Override Protocol
If any criterion cannot be satisfied, the project must explicitly report the failure and its scientific/legal implications. Proceeding with training requires formal executive override explicitly acknowledging the failure condition.
