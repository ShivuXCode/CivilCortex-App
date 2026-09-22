# CivilCortex ML Model Handover

This repository contains the definitive ML handover code and research documentation for the CivilCortex semantic segmentation model.

## 1. What this ZIP contains
This self-contained package includes the trained model weights, the exact inference scripts to load and run it, the model configuration, and the authoritative ML research record documenting its creation. The model weights must not be modified.

## 2. Final Model
**DeepLabV3+** architecture using an **EfficientNet-B4** backbone.

## 3. Input
**384x384 RGB** images.

## 4. Class Mapping
- 0 = Background
- 1 = Crack
- 2 = Spalling / Delamination
- 3 = Corrosion / Exposed Rebar
*(Ignore label during training: 255)*

## 5. Exact Final Test Metrics
Evaluated on the completely untouched 285-image test set:
- Mean Defect IoU = 0.6734
- Mean Defect Dice = 0.8046
- Crack IoU = 0.7057
- Spalling IoU = 0.6540
- Corrosion IoU = 0.6604

## 6. Exact command to verify model loading
From this directory, run the smoke test to load the checkpoint successfully:
```bash
python -m INFERENCE.inference
```

## 7. Python example to run inference
```python
import numpy as np
from PIL import Image
import torch
from INFERENCE.inference import load_civilcortex_model, run_inference, visualize_prediction

# 1. Load the model
model = load_civilcortex_model("MODEL/Phase6_ArchDeepLabEff_best.pth", device="cuda")

# 2. Run inference on a real image (returns the image array and the predicted 2D mask array)
img_array, pred_mask = run_inference("path_to_your_image.jpg", model, device="cuda", resolution=384)

# 3. Visualize the prediction
visualize_prediction(img_array, pred_mask, "output_visualization.png")
```

## 8. Python/PyTorch requirements
See `requirements.txt`.
- `torch>=2.0.0`
- `torchvision>=0.15.0`
- `segmentation-models-pytorch>=0.3.0`
- `albumentations>=1.3.0`
- `numpy`, `Pillow`, `matplotlib`

## 9. Important Note
The model weights (`MODEL/Phase6_ArchDeepLabEff_best.pth`) must **not** be modified, retrained, or altered. This is the final frozen checkpoint used for the research publication.

## 10. Research Record
The `RESEARCH/` folder contains the complete research record (`CIVILCORTEX_ML_RESEARCH_AND_HANDOVER.md`), including dataset discoveries, ablation results, and exhaustive error analysis.
