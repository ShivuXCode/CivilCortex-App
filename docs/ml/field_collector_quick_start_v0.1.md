# Field Collector Quick Start v0.1

This operational guide is for human field collectors capturing CivilCortex field dataset imagery.

## 1. How to Create/Select a Site
In the mobile app/interface, always start by selecting your geographic site. If the site does not exist, tap "Create New Site" and provide the exact location and structural type (e.g., "North Viaduct, Zone A").

## 2. How to Create/Select a Building
Select the continuous structure or building within the site. Never mix up buildings, as they ensure isolation for our machine learning test sets.

## 3. How to Identify a Structural Element
Log the floor/area/room and explicitly name the structural element you are inspecting (e.g., "Column C3", "Beam B12").

## 4. How to Register a New Physical Defect
When you discover a defect not previously logged, select "New Physical Defect". The system will mint a unique Defect ID for it.

## 5. How to Capture Images
- Capture a context image (zoomed out showing the defect on the structural element).
- Capture orthogonal (straight-on) detail images of the defect.
- Lock focus on the concrete texture.
- Do not use digital zoom; physically move closer.

## 6. How to Capture Calibration Evidence
Place a reference ruler strictly coplanar (flat) against the defect surface. Capture the image. Select the calibration status as `PHYSICAL_CALIBRATED` and enter the reference unit.

## 7. How to Add Observations Later
If you are returning to a previously logged defect, do NOT create a new defect. Use the app to search the structural element, select the existing Defect ID, and choose "Add New Observation".

## 8. How to Classify Defect Type
Tag the defect strictly as `crack`, `spalling`, `efflorescence`, or `hard_negative`. If it is a hard negative (e.g., a formwork seam or stain looking like a crack), log it explicitly as a hard negative.

## 9. How to Record Morphology
Add descriptive attribute tags for cracks (e.g., `horizontal`, `vertical`, `branching`). These are attributes, not separate defects.

## 10. How to Handle Uncertain Cases
Mark the morphology or identity as `UNCERTAIN`. Do not guess. Do not hallucinate occluded geometry.

## 11. How to Handle Privacy Concerns
Screen your framing. If a person's face, vehicle license plate, or private document is visible, re-frame the shot. If impossible, the image will be marked `REDACT` or `REJECT` in QC.

## 12. How to Submit for Annotation/Review
Verify the hierarchy (Site -> Building -> Element -> Defect ID). Save the draft and tap "Submit".

## 13. What Causes Rejection
QC will reject your image if it has motion blur, is out of focus, lacks context, captures private/unsafe data, or uses fabricated calibration. Rejection requires re-capture.

## 14. What NOT To Do
- Do NOT fabricate or estimate measurements without calibration.
- Do NOT mix up longitudinal defect IDs.
- Do NOT capture while walking (motion blur).
- Do NOT guess physical measurements from pixel photos.
