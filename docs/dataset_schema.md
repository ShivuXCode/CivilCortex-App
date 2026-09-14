# CivilCortex Dataset Schema

## Overview
This document defines the structural JSON metadata hierarchy that governs dataset identity. The schema supports strict data-leakage prevention by linking images to their physical origin rather than treating them as isolated arrays of pixels.

## Identity Hierarchy
Every dataset instance traces its origin via:
1. `source_id`: Origin dataset or field campaign (e.g., `civilcortex-field-24`).
2. `site_id` (Optional): The structural site or campus.
3. `building_id` (Optional): The specific structure.
4. `inspection_id` (Optional): The temporal inspection session.
5. `image_id`: Unique identifier of the photograph.

## Defect Instance Definition
- ONE physical visible defect = ONE `defect_instance_id`.
- The same physical crack photographed from three different angles corresponds to: 3 `image_id`s, but 1 shared `defect_instance_id`.

## Schema Fields

### ImageMetadata
- `source_id` (str)
- `site_id` (str, optional)
- `building_id` (str, optional)
- `inspection_id` (str, optional)
- `image_id` (str)
- `acquisition_date` (str, optional)
- `capture_device` (str, optional)
- `original_resolution` (str, optional)
- `preprocessing_history` (List[str])
- `annotation_version` (str, optional)
- `dataset_version` (str, optional)
- `image_width` (int)
- `image_height` (int)
- `quality_status` (enum: `PENDING`, `PASS`, `REJECTED`)
- `calibration` (CalibrationData)
- `defects` (List[DefectInstance])

### CalibrationData
- `is_calibrated` (bool): If False, pixels cannot be converted to mm.
- `reference_object` (str, optional): E.g., "Engineering Ruler".
- `pixels_per_mm` (float, optional).

### DefectInstance
- `defect_instance_id` (str): Links to the physical entity.
- `defect_type` (enum: `crack`, `spalling`, `efflorescence`)
- `morphology_tags` (List[str]): Attributes like `diagonal`, `branching`.
- `polygon` (List[List[float]]): Array of [x, y] vertex coordinates.
- `bounding_box` (List[float]): [xmin, ymin, xmax, ymax].
