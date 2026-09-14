# CivilCortex Dataset Split Policy

## 1. Group-Aware Split Generation
To ensure rigorous evaluation and prevent data leakage, the dataset split relies on a deterministic, group-aware algorithm. Random, image-level shuffling is strictly prohibited.

## 2. Split Hierarchy
The algorithm evaluates the most encompassing metadata available and assigns the entire group atomically to one of the splits (Train, Validation, or Test).

- **Tier 1 (Building/Site Isolation):** If `site_id` or `building_id` exists, all images associated with that structure remain in the same split. (Goal: Building-level generalization).
- **Tier 2 (Session Isolation):** If `inspection_id` exists, all burst-photos and session captures remain in the same split.
- **Tier 3 (Physical Defect Isolation):** If `defect_instance_id` exists, all images depicting the same physical crack remain in the same split.

## 3. Duplicate and Near-Duplicate Prevention
- **Exact Duplicates:** Detected via SHA-256 and removed.
- **Near-Duplicates:** Resized, recompressed, or burst-captured images are isolated via Perceptual Hashing (pHash) and `inspection_id` grouping.

## 4. Final Held-Out Evaluation
- The final Test split must contain structures/sites completely unrepresented in the Training and Validation splits.
- **External Generalization Set:** Where licensing permits, an external dataset (not collected by the CivilCortex team) may be designated as a supplementary evaluation set to verify cross-domain generalization. This set must never be used for hyperparameter tuning or model selection.

## 5. Dataset Versioning and Freeze
Each dataset version (e.g., `civilcortex-cv-v0.1`) requires a frozen split manifest. Once a Test set is established for a version, it is permanently locked to prevent iterative test-set tuning.
