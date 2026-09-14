# CivilCortex Dataset License Register

## Purpose
This register tracks the provenance, licensing, and explicitly verified usage rights of all public and external datasets considered for the CivilCortex production pipeline.

## 1. Production Training Candidates (License Cleared)

### DeepCrack
- **Source:** Liu et al. (GitHub Repository)
- **License:** MIT License
- **Commercial Use:** Permitted (MIT is permissive for commercial use and modification).
- **Redistribution:** Permitted with original copyright notice.
- **Image Count:** 537
- **Annotation Type:** Pixel-level binary segmentation masks
- **Defect Taxonomy:** Cracks
- **Domain:** Pavement and some structural concrete
- **Limitations:** Small scale; lacks morphology tags and spalling/efflorescence; no calibration data.

### SDNET2018
- **Source:** Utah State University (DigitalCommons)
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Commercial Use:** Permitted (with attribution).
- **Image Count:** 56,000 sub-images
- **Annotation Type:** Binary classification (crack / no-crack)
- **Defect Taxonomy:** Cracks and non-cracks
- **Domain:** Concrete bridge decks, walls, and pavements
- **Limitations:** Classification only (no segmentation masks). Cannot be used directly for CivilCortex segmentation unless manually re-annotated. Excellent source of negative examples.

### Mendeley Concrete Crack Images for Classification (CCIC)
- **Source:** Özgenel (Mendeley Data)
- **License:** CC BY 4.0
- **Commercial Use:** Permitted (with attribution).
- **Image Count:** 40,000 (20k positive, 20k negative)
- **Annotation Type:** Binary classification
- **Limitations:** Patches only. Good for robustness and hard negatives pretraining.

## 2. Research / Benchmark-Only Candidates

### CRACK500
- **Source:** Yang et al. (Temple University)
- **License:** Academic/Research (No explicit commercial license).
- **Commercial Use:** Not explicitly cleared.
- **Domain:** Pavement/Asphalt
- **Decision:** Restricted to benchmarking and research validation only.

### CODEBRIM (Concrete Defect Bridge Image Dataset)
- **Source:** Meta-vision / CVLab
- **License:** Academic/Non-commercial
- **Defect Taxonomy:** Cracks, Spalling, Efflorescence, Exposed Rebar
- **Decision:** Restricted to benchmarking only due to non-commercial license clause.

## 3. Rejected Candidates
Any dataset lacking a clear license file, lacking attribution guidelines, or hosted on unverified scraping hubs (e.g., generic Kaggle mirrors without source attribution) is inherently rejected.

## Dataset Comparison Matrix

| Dataset | Domain | License | Segmentation? | Spalling/Efflorescence? | Status |
|---|---|---|---|---|---|
| DeepCrack | Concrete/Pavement | MIT | Yes | No | Production |
| SDNET2018 | Bridges/Walls | CC BY 4.0 | No (Classification) | No | Production (Pretraining) |
| CCIC | Concrete | CC BY 4.0 | No (Classification) | No | Production (Pretraining) |
| CRACK500 | Pavement | Academic | Yes | No | Benchmark Only |
| CODEBRIM | Bridges | Non-commercial| Bounding Boxes | Yes | Benchmark Only |
