# Public-to-Field Domain Shift Plan v0.1

## 1. Objective
Identify and document the expected discrepancies (domain shift) between the public datasets used for Phase 10E-0 development training and the real-world field dataset that will be collected in Phase 10D.

## 2. Expected Differences

### A. Hardware and Cameras
- **Public Data**: Uncontrolled assortment of DSLRs, smartphones (from 2018), and scraped web images.
- **Field Data**: Standardized mobile collection utilizing modern lenses with specific focus requirements.

### B. Image Perspective and Distance
- **Public Data**: Highly variable distances; often scraped structural images taken from far away or zoomed in via digital zoom.
- **Field Data**: Protocol enforces orthogonal (perpendicular) capture at 0.5m - 2.0m using optical lenses.

### C. Environmental and Weathering Conditions
- **Public Data**: Limited metadata on geographic weathering. Often cleanly lit.
- **Field Data**: Will include harsh lighting, glare from wet concrete, shadows, and varying ages of civil infrastructure.

### D. Physical Calibration Availability
- **Public Data**: Contains no physical rulers or scale references. All measurements are assumed in pixels.
- **Field Data**: Requires validated `PHYSICAL_CALIBRATED` rulers placed coplanar with the defect to convert pixels to millimeters.

### E. Annotation Style
- **Public Data**: Many datasets use bounding boxes (e.g. DAMAGE_DETECTION) which poorly enclose thin, meandering cracks. Semantic masks often lack instance separation.
- **Field Data**: Enforces true tracing on visual evidence only (no dilation/hallucination) and distinguishes intersecting networks with `branching` morphology.

## 3. Implications
We explicitly state that **public-data model performance will not transfer directly to field data**. Baseline metrics from SDNET2018 or RC1841 are development benchmarks. The true efficacy of the model, and the selection of the final production architecture, is completely dependent on measuring and addressing this domain shift using the held-out real-world field dataset.
