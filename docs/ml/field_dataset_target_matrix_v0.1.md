# CivilCortex Field Dataset Schema & Targets v0.1

## 1. Dataset Target Matrix
*(See `ml_pipeline/dataset/field_dataset_target_matrix.json` for structured data)*

**MINIMUM ACCEPTANCE TARGET**
- 10 distinct sites/structures.
- 2,000 unique physical defect instances.

**RECOMMENDED COLLECTION TARGET**
- 20 distinct sites/structures.
- 3,500 physical defect instances.
- 15,000 total images (accounting for multi-view, longitudinal, and rejected captures).

**DEFECT DISTRIBUTION**
- Crack: 40%
- Spalling: 20%
- Efflorescence: 20%
- Hard Negatives: 20%

**MORPHOLOGY DISTRIBUTION (Cracks)**
- Ensure minimum 20% representation across each attribute: Horizontal, Vertical, Diagonal, Branching, Irregular.

**DIVERSITY**
- Minimum 3 distinct camera hardware configurations.
- Mix of indoor/outdoor, daylight/artificial lighting.

## 2. Metadata Schema
*(See `ml_pipeline/dataset/field_collection_schema.json` for structured data)*

Required core identifiers: `source_id`, `site_id`, `building_id`, `floor_id`, `area_id`, `structural_element_id`, `inspection_id`, `observation_id`, `image_id`.

## 3. Train / Validation / Test Strategy
Splitting MUST be performed before final collection processing, prioritizing isolation from top to bottom:
1. SITE / BUILDING isolation (Test set MUST contain genuinely unseen buildings).
2. INSPECTION / SESSION isolation.
3. DEFECT IDENTITY isolation (Same physical crack cannot be in Train and Test).
4. IMAGE isolation.

Multiple photographs or longitudinal repeat observations of the same physical defect MUST remain strictly in the exact same split.
