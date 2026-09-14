# CivilCortex Longitudinal Collection Protocol v0.1

## 1. Overview
Longitudinal monitoring is a primary differentiator for CivilCortex. This protocol defines how to capture repeated observations of the same physical defect over time to track progression.

## 2. Subset Selection
Designate a specific subset of structures for longitudinal monitoring. The subset must include:
- Stable cracks.
- Potentially changing/progressing cracks.
- Repaired cracks (where ethically and practically available).
- Diverse environmental exposures.

## 3. Data Integrity
For each repeat observation, the data MUST preserve the identical:
- `site_id`
- `building_id`
- `floor_id`
- `area_id`
- `structural_element_id`
- `defect_instance_id` (The Crack Identity)

A NEW `inspection_id` and `observation_id` are created for the new visit.

## 4. Capture Repeatability
- Follow-up images must attempt to match the original focal length, camera distance, and viewing angle.
- Do NOT assume a later image is the same crack merely because it visually resembles an earlier one. For ambiguous matches, mark as `CANDIDATE_MATCH` and require engineering confirmation.
- Do NOT create synthetic progression by modifying images.

## 5. Frequency
Recommended repeat intervals are 1-month, 3-month, or 6-month cycles, dictated by site access rather than strict ML requirements.
