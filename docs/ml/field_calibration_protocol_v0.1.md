# CivilCortex Field Calibration Protocol v0.1

## 1. Purpose
CivilCortex requires calibrated physical measurements (width/length in mm). We cannot infer millimeter dimensions from arbitrary uncalibrated photographs.

## 2. Acceptable Calibration References
Every image intended for physical measurement must include one of the following:
- CivilCortex custom 10cm/20cm rigid target.
- Standard metric engineering ruler.
- Verified laser scale (dot projection).

## 3. Placement Requirements
The calibration reference must be:
1. **Coplanar:** Positioned exactly on the structural surface, directly adjacent to the defect. It must lie on the same focal plane as the crack.
2. **Unobscured:** Fully visible to the camera without glare washing out the scale markers.

## 4. Metadata States
The system must explicitly distinguish calibration status:
- `PHYSICAL_CALIBRATED`: Reference is present, coplanar, and extracted.
- `PIXEL_ONLY`: No reference present.
- `ESTIMATED`: Depth-camera or LiDAR estimated (if supported later).
- `UNAVAILABLE`: Cannot be calculated.

Do NOT label an uncalibrated measurement as `PHYSICAL_CALIBRATED`.
