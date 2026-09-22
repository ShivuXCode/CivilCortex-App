# RESEARCH FINAL RESULTS

## Best Configuration
- Experiment: Phase6_ArchDeepLabEff
- Architecture: deeplabv3plus
- Backbone: efficientnet-b4
- Resolution: 384
- Loss: FocalDice

## Validation Ablation Table
| Experiment | Architecture | Backbone | Resolution | Loss | Val mIoU | Val Dice | Crack IoU | Spalling IoU | Corrosion IoU |
|-|-|-|-|-|-|-|-|-|-|
| Phase3_Baseline | deeplabv3plus | resnet50 | 384 | FocalDice | 0.5661970376968384 | 0.7190355658531189 | 0.6829206347465515 | 0.4699757397174835 | 0.5456947088241577 |
| Phase4_Res512 | deeplabv3plus | resnet50 | 512 | FocalDice | 0.5479847192764282 | 0.7065256834030151 | 0.6188573837280273 | 0.4930372536182403 | 0.532059371471405 |
| Phase5_LossCE | deeplabv3plus | resnet50 | 384 | CrossEntropy | 0.6151566505432129 | 0.7591085433959961 | 0.7077457904815674 | 0.525811493396759 | 0.6119126677513123 |
| Phase5_LossTversky | deeplabv3plus | resnet50 | 384 | TverskyFocal | 0.5601911544799805 | 0.7121661901473999 | 0.7134437561035156 | 0.4901449680328369 | 0.4769846200942993 |
| Phase5_LossWeightedCE | deeplabv3plus | resnet50 | 384 | WeightedCrossEntropyDice | 0.6109837293624878 | 0.7559818625450134 | 0.7147677540779114 | 0.548457682132721 | 0.5697256326675415 |
| Phase6_ArchUNet | unet | resnet50 | 384 | FocalDice | 0.5448809862136841 | 0.7023696303367615 | 0.6484248042106628 | 0.5161473155021667 | 0.4700707793235779 |
| Phase6_ArchDeepLabEff | deeplabv3plus | efficientnet-b4 | 384 | FocalDice | 0.6256738901138306 | 0.7687327265739441 | 0.6851887702941895 | 0.5713486671447754 | 0.6204841136932373 |
| Phase6_ArchSegFormer | segformer | mit_b3 | 384 | FocalDice | 0.5580520629882812 | 0.7162148356437683 | 0.5800498723983765 | 0.5504075884819031 | 0.543698787689209 |


## Final Test Results
- Mean Defect IoU: 0.6734
- Mean Defect Dice: 0.8046
- Crack IoU: 0.7057
- Spalling IoU: 0.6540
- Corrosion IoU: 0.6604
