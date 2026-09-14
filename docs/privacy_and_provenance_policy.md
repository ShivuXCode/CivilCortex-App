# CivilCortex Privacy and Provenance Policy

## 1. Privacy Standards
The dataset must not unnecessarily ingest Personally Identifiable Information (PII).
- **Prohibited Content:** Recognizable faces, vehicle license plates, personal documents, and explicit residential addresses where inappropriate.
- **Enforcement:** Privacy screening is the absolute first step in the data pipeline. Images containing PII must be rejected or permanently redacted *before* entering the annotation workflow.

## 2. Data Provenance
Every image in the CivilCortex dataset must maintain strict, traceable provenance. Silent alteration of source data is prohibited.

The metadata schema guarantees the preservation of the following records:
- **`source_id`:** Original external dataset or internal field campaign identifier.
- **`site_id` / `building_id` / `inspection_id`:** Structural and temporal context.
- **`image_id`:** Unique capture identifier.
- **`defect_instance_id`:** The physical defect link.

## 3. Preservation of Public Dataset Attribution
When importing images from publicly cleared datasets (e.g., SDNET2018):
- The original source attribution must never be removed.
- Re-annotation (e.g., creating segmentations over a SDNET2018 image) does not void the original license obligations. The modified artifact metadata must reflect both the original CC BY 4.0 license and the subsequent preprocessing history.

## 4. Required Versioning Metadata
The exact history of an image is tracked via:
- `acquisition_date`: Original capture timestamp.
- `capture_device`: Sensor/hardware details.
- `original_resolution`: Native capture size.
- `preprocessing_history`: Log of any crops, blurs, or color corrections applied.
- `annotation_version`: Hash or ID of the segmentation polygon state.
- `dataset_version`: Semantic version of the dataset release in which the image was locked (e.g., `civilcortex-cv-v0.1`).
