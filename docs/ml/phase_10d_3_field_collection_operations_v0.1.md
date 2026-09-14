# Field Collection Operations Specification v0.1 (Phase 10D.3)

## 1. Purpose
To define the complete operational procedure and software infrastructure required for human data collectors to safely, accurately, and reproducibly acquire the CivilCortex field dataset. 

## 2. Approved Dataset Targets
- **Total Unique Physical Defects**: ≥3,100
- **Crack Minimum**: ≥1,500
- **Spalling Minimum**: ≥800
- **Efflorescence Minimum**: ≥800
- **Hard Negatives Minimum**: ≥800 (Separate from physical defects)
- **Minimum Sites/Structures**: ≥10 distinct sites

## 3. Site Selection Strategy
Sites must not be selected by convenience. They must provide balanced exposure across environmental conditions, concrete formulations, structure types (bridges, retaining walls, viaducts), and lighting conditions.

## 4. Building Selection Strategy
Building isolation prevents test set leakage. A single building or continuous concrete structure cannot span training, validation, and test sets.

## 5. Floor/Area/Room Recording
Collectors must document the structural hierarchy required to maintain physical defect identity mapping.

## 6. Structural-Element Identification
Structural elements (e.g., Column C3, Beam B12) must be explicitly named to group defects originating from the same member.

## 7. Defect Identification
Visual evidence of a crack, spalling, or efflorescence. Must adhere to defect taxonomy definitions. Intersecting crack networks should be treated as one physical/visual instance with branching morphology, where appropriate. Disconnected cracks are separate physical defects.

## 8. Image Capture Protocol
Raw field image → source storage → SHA-256 → perceptual hash → metadata validation → privacy review → quality review → dataset registration → annotation.

## 9. Image Framing Requirements
Ensure defect is fully framed where possible. Use multiple overlapping detail shots for massive defects.

## 10. Distance/Angle Guidance
Capture at an orthogonal (perpendicular) angle to the surface to minimize perspective distortion, ideally from 0.5m to 2.0m distance.

## 11. Lighting Guidance
Avoid direct flash bounce. Use diffuse, off-axis lighting if necessary. Do not discard shadows if they represent realistic operational conditions.

## 12. Focus/Sharpness Requirements
Camera must lock focus on the concrete surface texture, not background or foreground elements.

## 13. Avoiding Reflections/Glare
If water or efflorescence causes glare, adjust angle minimally. Do not manipulate images post-capture.

## 14. Avoiding Motion Blur
Do not capture while walking. Image must be rejected by QC if motion blur obscures fine crack detail.

## 15. Avoiding Unnecessary Zoom
Use optical lens capture; avoid digital zoom.

## 16. Context Images vs Defect-Detail Images
- **Context image**: Shows the defect relative to the structural element (often uncalibrated).
- **Defect detail image**: Focused on the specific defect boundaries.

## 17. Calibration Capture Procedure
Physical measurements are permitted only when validated calibration exists. A physical scale or reference marker must be placed.

## 18. Scale-Reference Placement
The reference object (e.g., calibration ruler) must be placed directly against the surface near the defect without occluding it.

## 19. Coplanarity Requirement
The calibration reference must be strictly coplanar with the defect surface.

## 20. Calibration Metadata
Record calibration type, reference dimension (e.g., 50mm ruler), measurement unit, and status.

## 21. Defect Identity Assignment
Do not create ambiguous 'new' or fake IDs (e.g., `crack_id = 0`). The system explicitly mints and tracks a unique UUID for each physical defect.

## 22. Multiple Observations of the Same Physical Defect
Multiple images of the same defect from different angles, or taken over time, belong to the *same* physical defect identity. They are distinct `observations`.

## 23. Longitudinal Revisit Protocol
Subsequent inspections of previously captured defects must use contextual matching (site, element, location) to link the new observation to the existing physical defect ID.

## 24. Hard-Negative Collection
Collect at least 800 challenging non-defect examples (joints, seams, shadows, stains). They must be explicitly classified as hard negatives and excluded from the physical-defect total.

## 25. Privacy Screening
Images must be reviewed. Explicit privacy states: `ACCEPT`, `REDACT`, `REJECT`. Screen for faces, licenses, and private information.

## 26. Consent/Permission
Do not fabricate consent. Record explicit ethics/consent metadata when required by site ownership.

## 27. Unsafe-Area Restrictions
Collectors must not enter unsafe structural zones to acquire data.

## 28. Collector Metadata
Record pseudonymous collector ID and hardware used.

## 29. Upload Procedure
Images upload via API, establishing immediate hash immutability in object storage.

## 30. QC Workflow
Submitted → Pending QC Review → Accepted / Rejected.

## 31. Rejection/Re-capture Workflow
If rejected for blur/privacy/framing, collector must re-acquire the observation. Do not manipulate the rejected image.

## 32. Data Provenance
Full traceability from collector → raw image → hash → metadata → observation.

## 33. Dataset Versioning
Immutable versioning for ML iterations. (e.g., `v1.0.0`, schema version, manifest hash).

## 34. Chain of Custody
No manual file system manipulation. All images pass through the API ingestion gate.

## 35. Field Failure Handling
Hardware crashes, upload timeouts, and offline capture modes are explicitly tracked.

---
**CRITICAL LIMITATION**: Never infer physical crack length or width from an arbitrary photograph. Physical measurements require validated calibration.
