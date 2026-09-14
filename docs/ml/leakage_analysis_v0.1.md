# CivilCortex Leakage Analysis v0.1

## Overview
Data leakage occurs when the model trains and tests on images of the identical physical crack, or cracks from the identical building/site, resulting in artificially inflated accuracy metrics. This report analyzes the 6 downloaded public datasets for structural leakage risk.

## 1. Source Grouping Availability

| Dataset | Structural Identity / Grouping | Leakage Risk |
| :--- | :--- | :--- |
| **SDNET2018** | **HIGH**. Bridge deck IDs are encoded directly in the filenames (e.g., `7001`). Grouping is possible. | **LOW** (If properly grouped in splits) |
| **CCIC** | **NONE**. The dataset provides 40,000 cropped images. Filenames do not map to the 458 original source images. | **VERY HIGH** |
| **RC1841** | **NONE**. No physical structure metadata is provided. | **HIGH** |
| **DamageDetection** | **NONE**. | **HIGH** |
| **MDMCS** | **NONE**. | **HIGH** |
| **CICS** | **NONE**. | **HIGH** |

## 2. Leakage Status
For 5 out of the 6 datasets, building-level generalization **CANNOT BE VERIFIED**. The only structural defense we currently have for these 5 datasets is deterministic Perceptual Hashing (pHash) to remove exact or near-duplicate crops of the exact same scene. However, this does not prevent two *different* angles of the same crack from leaking across the train/test boundary.

## 3. Recommended Strategy
1. **SDNET2018**: Group strictly by Bridge ID during splitting.
2. **Other Datasets**: Rely on pHash `duplicate_clusters.json` to purge all exact duplicates (distance 0) and likely scene duplicates (distance <= 8).
3. **Field Data**: Future field data MUST include `site_id` and `defect_instance_id` to guarantee zero-leakage splits.
