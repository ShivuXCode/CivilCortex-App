# CivilCortex Human Field-Collection Checklist

## 1. Safety and Permission
- Ensure you have the legal right and safety clearance to photograph the structure.
- **Privacy:** Avoid capturing faces, license plates, personal documents, and explicit residential addresses.

## 2. Capture Protocol
- Ensure adequate lighting. Use flashlights for dark areas.
- Do not blur or shake the camera. Blurry images will be automatically rejected.
- Capture at the highest native resolution available on your device.

## 3. Required Metadata Logging
For every session/image, you MUST record the following context (via the collection app or logbook):
- [ ] `site_id` (e.g., Campus North)
- [ ] `building_id` (e.g., Reactor Block B)
- [ ] `floor_id` (e.g., Level 2)
- [ ] `area_id` (e.g., Stairwell 4)
- [ ] `structural_element` (e.g., Column, Beam, Wall, Slab, Plaster). Do NOT guess. If unknown, record "Unknown".
- [ ] `inspection_id` / Session ID
- [ ] Capture Date and Time
- [ ] Device used (e.g., iPhone 14 Pro, Sony A7III)
- [ ] Physical `defect_instance_id` (assign a persistent ID for the specific crack/defect you are photographing)

## 4. Diversity and Defect Identity
- **Multiple Views:** Capture multiple angles and distances of the same defect, but ensure they are all logged under the SAME `defect_instance_id`.
- **Do not intentionally fabricate defects:** Do not alter crack geometry, scrape surfaces, or draw on the wall.
- **Hard Negatives:** Intentionally photograph construction joints, formwork seams, paint lines, dirt, shadows, and scratches. Log these explicitly as "Hard Negatives".

## 5. Calibrated Measurement Protocol
If you are collecting data for the Measurement Validation subset:
- [ ] Place a physical engineering ruler or calibrated target perfectly flush against the surface, adjacent to the crack.
- [ ] Ensure the camera is exactly perpendicular to the surface to minimize perspective distortion.
- [ ] Record the true physical ground truth measurement (e.g., maximum width = 1.2mm) in your log.
- [ ] Explicitly tag the image as "Calibrated". Uncalibrated images cannot be used for physical measurement validation.
