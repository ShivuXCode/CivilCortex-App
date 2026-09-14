# CivilCortex Duplicate Analysis v0.1

## Overview
A perceptual hash (pHash) analysis was executed across 115,183 valid images to determine duplication rates. Duplicates introduce data leakage if present across train/test boundaries and artificially inflate apparent dataset size. 

## 1. Methodology
- **Algorithm**: `imagehash.phash` (64-bit fingerprint based on Discrete Cosine Transform).
- **Metric**: Hamming distance between binary hashes.
- **Thresholds**: 
  - `Distance == 0`: EXACT_DUPLICATE (or trivially resized/recompressed)
  - `Distance <= 4`: LIKELY_DUPLICATE (minor watermark/compression differences)
  - `Distance <= 8`: LIKELY_SAME_SCENE (different crop/lighting of identical physical area)
  - `Distance <= 12`: POSSIBLE_SAME_PHYSICAL_DEFECT (requires human review)

## 2. Quantitative Results
- **Total images processed**: 115,183
- **Unique perceptual hashes**: 101,428
- **Exact duplicate images**: 13,755
- **Within-dataset exact duplicates**: 12,665
- **Cross-dataset exact duplicates**: 1,090
- **Near-duplicate clusters detected**: 8,955

## 3. Analysis & Strategy
The presence of 1,090 cross-dataset exact duplicates proves that researchers have been sampling identical source images (likely from CRACK500 or SDNET) and re-uploading them as "novel" datasets (e.g., in CCIC and CICS). 

**Recommended Action**:
For model training, any image path flagged in `duplicate_clusters.json` MUST be purged from the dataset manifolds such that only one representative image per cluster remains, ensuring no cluster spans both the Train and Test split.
