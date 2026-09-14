# CivilCortex CV Annotation Standard Operating Procedure (SOP)

## 1. Objective
To collect a robust dataset for the Computer Vision model capable of identifying defect instances (cracks, spalling, efflorescence) and delineating them using precise instance segmentation polygon masks.

## 2. Taxonomy & Morphological Tags
- **Classes:** `crack`, `spalling`, `efflorescence`
- **Crack Morphology Tags (Multi-Label):** `diagonal`, `horizontal`, `vertical`, `branching`, `irregular`

*Note: Do not annotate "shear failure" or "flexural failure". Only describe what is visually present.*

## 3. Mask Geometry Guidelines
1. **Tightness:** Polygon points must snap tightly to the visible outer boundaries of the defect.
2. **Width Precision:** Ensure the mask width exactly reflects the visible crack width in the image. Bounding boxes are strictly prohibited.
3. **Continuity:** If a crack branches, annotate the entire continuous structure as a single instance.
4. **Overlaps:** If two distinct cracks intersect, annotate them as two separate overlapping polygons.

## 4. Calibration References
- If a known reference object (e.g., standard ruler, calibration target) is present in the focal plane of the crack, annotate the object with a bounding box and assign it the class `calibration_reference`. 
- Input the physical dimensions of the object in the annotation metadata where possible.

## 5. Quality Control
- **Format:** COCO JSON.
- **Review:** Every 10th image must be peer-reviewed for mask tightness by a lead annotator.
- **Group-Aware Splitting:** During dataset export, images must be tagged with their source `building_id` or `inspection_id` to ensure proper group-aware splits.
