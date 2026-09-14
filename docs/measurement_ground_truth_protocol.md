# CivilCortex Measurement Ground Truth Protocol

## 1. Goal
Establish a scientifically rigorous tier of calibrated data to validate the physical measurement engine. The CV output must strictly distinguish between a raw "pixel measurement", a "physically calibrated measurement", an "estimated measurement", and an "unavailable measurement".

## 2. Dataset Tiers

### Tier A: Detection & Segmentation Dataset
- **Purpose:** Train the model to identify defects and morphology.
- **Calibration Status:** OPTIONAL. Uncalibrated images are fully acceptable.

### Tier B: Measurement Validation Dataset
- **Purpose:** Provide a ground-truth benchmark for evaluating the pixel-to-millimeter conversion accuracy.
- **Calibration Status:** MANDATORY.

## 3. Tier B Capture Protocol
Every calibrated sample must visually capture a physical scaling reference.
- **Reference Object:** An engineering crack ruler, surveying scale, or standard calibrated target.
- **Placement:** The reference must be placed absolutely flush with the inspected surface, parallel to the image plane where possible.
- **Orientation/Distance:** The camera must be positioned perpendicular to the surface. Capture distance and camera angle should be recorded in metadata if depth sensors are used.

## 4. Ground Truth Annotations
For Tier B images, the annotator must record the verifiable physical ground truth (not just trace pixels).
- **Physical Crack Width:** Maximum width in millimeters (mm).
- **Physical Crack Length:** Cumulative length in millimeters (mm).
- **Measurement Tolerance:** Stated uncertainty (e.g., ± 0.2mm).

## 5. Scientific Boundaries
- Pixel length/width extracted from a segmentation mask is NEVER equivalent to physical length/width without a calibrated spatial reference.
- The system must not claim physical millimetre measurements from an arbitrary, uncalibrated image.
