# CivilCortex Field Data Collection Specification v0.1

## Overview
The public dataset audit (Phase 8) has determined that the existing 113,883 images are strictly insufficient for production ML deployment due to a lack of physical calibration, structural leakage prevention, absence of efflorescence instances, and unverified instance-level spalling coverage.

To transition CivilCortex into a robust structural inspection tool, we must collect *Field Data* that adheres to rigorous capture and metadata standards.

## 1. Required Metadata Schema
Every field image must be accompanied by the following deterministic schema to ensure leakage-free data splits and longitudinal monitoring support:

### Identity & Grouping
- `source_id`: The acquiring engineer/organization.
- `site_id`: Broad campus or infrastructure complex.
- `building_id`: Specific physical building.
- `inspection_id`: The temporal session ID of the inspection.
- `image_id`: Unique file identity.
- `defect_instance_id`: A UUID tracking the **exact physical crack** across multiple images and longitudinal visits.

### Contextual Location
- `floor`: Floor index.
- `area`: Room or specific zone.
- `structural_element`: (e.g., column, beam, slab, retaining wall).
- `material`: (e.g., reinforced concrete, masonry).

### Acquisition & Calibration
- `capture_device`: Camera model and lens details.
- `acquisition_date`: ISO 8601 timestamp.
- `calibration_reference`: Must state the physical reference present in the image (e.g., "CivilCortex 10cm Target", "Tape Measure", "Laser Scale").
- `reference_plane`: Boolean indicating whether the calibration reference is coplanar with the defect.

## 2. Longitudinal Monitoring Constraints
To support progression tracking (e.g., crack propagation over time):
1. **Identical Viewport:** Follow-up images must attempt to match the original focal length, distance, and angle.
2. **Persistence:** The `defect_instance_id` MUST be preserved across time. Do not mint a new defect ID for a follow-up image of the same crack.

## 3. Calibration Requirements
Physical measurements (width/length in mm) **must not be generated** without a calibration reference. 
Field images intended for measurement validation must include a rigid calibration target (e.g., a high-contrast checkerboard or ruler) positioned exactly on the structural surface, adjacent to the crack, ensuring they share the same focal plane.

## 4. Target Acceptance Criteria (Initial Batch)
- Minimum 10 distinct sites/structures.
- Minimum 2,000 unique physical defect instances.
- At least 20% negative instances (construction joints, formwork marks, water stains).
- At least 10% representation each for horizontal, vertical, diagonal, and branching morphology.
- At least 3 genuinely different sensor hardware configurations.
