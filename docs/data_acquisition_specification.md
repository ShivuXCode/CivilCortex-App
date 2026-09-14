# CivilCortex Data Acquisition Specification

## 1. Goal
Establish a scientifically valid, legally usable, and structurally diverse dataset of civil engineering defects prior to model training.

## 2. Recommended Data-Source Mix
Due to the limitations of public datasets (pavement-heavy, unclear licenses, lacking spalling/efflorescence segmentations), the final CivilCortex dataset will rely on a hybrid acquisition strategy:

- **Primary Source (70%):** CivilCortex Field-Collected Imagery. Essential for matching our production target domain (walls, columns, structural slabs) and collecting spalling/efflorescence data.
- **Secondary Source (20%):** Re-annotated public commercial-cleared datasets (e.g., DeepCrack segmentation, SDNET2018 negative samples).
- **Hard Negatives (10%):** Explicitly curated images of non-defects.

## 3. CivilCortex Field-Collection Protocol (First Batch Quotas)

The initial collection batch focuses on ensuring baseline diversity.

### Structural Diversity Targets (Minimums)
- **10 Distinct Sites/Buildings:** To ensure structural and architectural variance.
- **2,000 Unique Physical Defect Instances:** Sourced across the sites.
- **Class Representation:**
  - Cracks: 60%
  - Spalling: 20%
  - Efflorescence: 20%
- **Morphology Representation:** Minimum 10% for each tag (horizontal, vertical, diagonal, branching, irregular).

### Camera and Device Protocol
- At least 3 genuinely different sensor configurations must be used (e.g., iPhone 13 Pro, Samsung S23, DSLR/Drone).
- **Prohibition:** Artificial camera diversity (e.g., algorithmic resizing, noise injection) does not satisfy this quota.

### Environmental Capture Protocol
Capture each site under varying conditions:
- Indoor (low light, shadows, flashlight).
- Outdoor (direct sunlight, overcast, weathered surfaces).
- Surfaces: Plaster, exposed concrete, masonry, painted surfaces.

## 4. Negative and Hard-Negative Strategy
The CV system must learn that a dark linear feature is not always a crack. The collection protocol requires intentionally photographing:
- Surface joints, formwork seams, construction lines.
- Paint lines, scratches, water marks, discoloration.
- Dirt, stains, shadows from wires/fences.

## 5. Privacy and Rejection
Images containing faces, license plates, explicit addresses, or personal documents must be rejected at the time of capture.

## 6. Image Quality vs. Training Resolution
- **Original Capture Quality:** High-resolution native capture is required. Do not discard high-res images simply because they exceed the neural network's input tensor size (e.g., 640x640).
- **Prohibition:** Do not use artificial upscaling to recover missing visual information in blurry images. Blurry images without visible defect definition must be rejected.
