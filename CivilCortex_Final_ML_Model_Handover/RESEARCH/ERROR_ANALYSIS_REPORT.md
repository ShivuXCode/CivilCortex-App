# CivilCortex Error Analysis

## 1. Objective
Perform a rigorous, read-only analysis of the final selected model on the 285-image untouched Test set, without modifying ground truth or hyperparameters.

## 2. Final Model
- Checkpoint: `Phase6_ArchDeepLabEff_best.pth`
- Architecture: `deeplabv3plus`
- Backbone: `efficientnet-b4`

## 3. Overall Performance
- Test images: 285
- Mean Defect IoU: 0.6734
- Mean Defect Dice: 0.8046

## 4. Per-Class Performance
- Crack IoU: 0.7057
- Spalling IoU: 0.6540
- Corrosion IoU: 0.6604

## 5. Confusion Matrix Analysis
**Dominant Confusion Pairs**:
- **Spalling vs. Corrosion**: 467,694 Spalling pixels were predicted as Corrosion, and 531,196 Corrosion pixels were predicted as Spalling. This indicates massive boundary ambiguity between these co-occurring defects.

## 6. False Positive & False Negative Patterns
- **Crack**: False Positives (236k pixels) heavily outnumber False Negatives (74k pixels). The model suffers from **over-segmentation**, likely misclassifying concrete joints or dark surface textures as cracks.
- **Spalling/Corrosion**: Both suffer from high FP and FN, largely driven by the inter-class confusion mentioned above.

## 7. Defect Size Analysis
Performance heavily degrades for small defect instances across all classes:
- **Corrosion**: Small (IoU 0.29) vs Large (IoU 0.76)
- **Crack**: Small (IoU 0.45) vs Large (IoU 0.95)
- **Spalling**: Small (IoU 0.48) vs Large (IoU 0.82)

## 8. Observed Failure Modes
1. **Inter-class Ambiguity (Spalling/Corrosion)**: Severe boundary mismatch where exposed rebar and concrete spalling meet.
2. **Crack Over-segmentation**: False positives triggered by background texture and structural joints.
3. **Small Defect Missing**: Small fragments of damage are entirely missed or under-segmented.

## 9. Visualizations
All 4-panel contact sheets (Original | GT | Pred | Error Map) have been generated and categorized.
- Best overall cases: `visualizations/best_cases/`
- Worst overall cases: `visualizations/worst_cases/`
- Class-specific worst cases: `visualizations/crack/`, `visualizations/spalling/`, `visualizations/corrosion/`
