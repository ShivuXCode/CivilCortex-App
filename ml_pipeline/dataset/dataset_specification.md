# CivilCortex Dataset Specification

## 1. Dataset Purpose
To train, validate, and test binary defect classifiers and morphological segmentation models (e.g. cracks, spalling) for civil engineering structures. The dataset aims to provide high-fidelity pixel masks rather than bounding boxes to support downstream measurement engines.

## 2. Supported Defect Types
- `crack`: Visible structural or surface cracking.
- `spalling`: Concrete surface flaking or delamination.
- `efflorescence`: Crystalline salt deposits.

## 3. Crack Morphology Labels
- `diagonal`, `horizontal`, `vertical`, `branching`, `irregular`
*Note: A single defect can have multiple morphology labels.*

## 4. Annotation Format and Semantics
Annotations must be provided as polygonal segmentations (COCO JSON format or similar) tightly bounding the defect. Bounding box-only annotations are insufficient for training measurement networks.

**Semantics:** A physical defect should remain exactly ONE annotated instance. Do NOT create separate segmentation masks merely because the same crack has multiple morphology tags. Morphology remains an attribute/tag of the single visual defect instance. For example, a single `crack` instance can have tags `["diagonal", "branching"]`.

## 5. Image Requirements
- **Format:** JPG, JPEG, PNG, WEBP
- **Minimum Resolution:** 480x480 pixels
- **Lighting:** Adequate exposure; images with extreme shadows or glare should be excluded.

## 6. Segmentation Requirements
Polygons must adhere strictly to the boundaries of the visible defect without excessive padding (≤ 3 pixels from the true boundary edge). Self-intersecting polygons are prohibited.

## 7. Calibration Metadata
Calibration is NOT a universal dataset-readiness requirement.

- **General detection/segmentation images:** Calibration is `OPTIONAL`. Useful uncalibrated images must not be discarded simply because they lack a ruler/reference object.
- **Measurement-validation subset:** Calibration/reference is `REQUIRED`. Only calibrated/reference-backed samples should be used for physical measurement ground truth.

## 8. Provenance & Usage Rights
- Sources must be fully documented.
- Synthetic/web-scraped data without explicit license rights is prohibited.
- Images containing personally identifiable information (PII) must be redacted.

## 9. Acceptable Sources
- Authorized structural inspection imagery.
- Open-source engineering datasets with commercial use permissions.

## 10. Prohibited Sources
- Unverified web scraping.
- Generative AI synthetic images without physical ground truth validity.
