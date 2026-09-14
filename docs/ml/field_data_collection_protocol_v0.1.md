# CivilCortex Field Data Collection Protocol v0.1

## 1. Objective
To collect a robust, leakage-free, fully calibrated dataset of concrete structural defects (cracks, spalling, efflorescence) and hard negatives across diverse real-world environments.

## 2. Directory Structure & Immutable Captures
All collected field data must conform to the following directory structure:
```
field_data/
    raw/
        site_<id>/
            building_<id>/
                inspection_<id>/
                    images/
                    metadata/
                    calibration/
    annotations/
    reviewed/
    manifests/
    quality_reports/
```
**CRITICAL RULE:** The `raw/` directory is strictly immutable. Original captures must never be resized, overwritten, or modified.

## 3. Physical Hierarchy Definition
Field data is organized hierarchically to preserve the distinction between an image, an observation, and a physical defect instance:

`SITE -> BUILDING -> FLOOR -> AREA -> STRUCTURAL ELEMENT -> DEFECT -> OBSERVATION -> IMAGE`

- **CRACK (`defect_instance_id`)**: The persistent physical identity of the defect on the wall.
- **OBSERVATION (`observation_id`)**: The temporal state of that crack during a specific inspection.
- **IMAGE (`image_id`)**: One of potentially multiple photographs taken during that observation.

## 4. Multi-Image Capture for One Defect
A single physical defect must often be photographed multiple times during one observation. Recommended sequence:
1. Overview/Context image (showing element geometry).
2. Medium-distance image.
3. Close-up image.
4. Calibrated measurement image.

All images of the same physical defect must share the exact same `defect_instance_id`. They do NOT become separate physical defects merely because there are multiple photographs.

## 5. Hard Negative Collection
To reduce false positives, collectors must explicitly target and photograph non-defect surfaces that visually resemble defects, labeled appropriately:
- Construction/control joints, seams, formwork marks.
- Paint lines, stains, dirt, shadow lines.
- Scratches, wire shadows, water marks.

## 6. Thin Crack Coverage
- Target thin cracks explicitly. 
- Do NOT artificially widen cracks in images or annotations.
- Ensure camera focus and resolution are sufficient to capture the thin evidence natively.

## 7. Schema Gap Identification
Before execution, note a gap in the current `metadata_schema.py`: 
- `floor_id`, `area_id`, `structural_element_id`, and `observation_id` are currently missing from `ImageMetadata`. 
- `metadata_schema.py` must be updated to match the `field_collection_schema.json` prior to ingestion.
