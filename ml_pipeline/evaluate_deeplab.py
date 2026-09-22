import os
import torch
from torch.utils.data import DataLoader
import numpy as np
import segmentation_models_pytorch as smp

# Re-use the dataset and transforms from train_deeplab
from train_deeplab import CivilCortexDataset, get_validation_augmentation, CLASSES, IGNORE_INDEX

IMG_SIZE = 384
BATCH_SIZE = 1
DEVICE = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
DATA_DIR = "dataset/segmentation"
MODEL_PATH = "../backend/models/Phase6_ArchDeepLabEff_best.pth"

def main():
    print(f"Evaluating CivilCortex DeepLabV3+ on {DEVICE}...")
    
    # 1. Load Model
    model = smp.DeepLabV3Plus(
        encoder_name="efficientnet-b4",
        encoder_weights=None,
        in_channels=3,
        classes=CLASSES
    ).to(DEVICE)
    
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model weights not found at {MODEL_PATH}")
        return
        
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.eval()
    print("Model loaded successfully.")
    
    # 2. Data Loader
    test_dir_img = os.path.join(DATA_DIR, "test", "images")
    test_dir_mask = os.path.join(DATA_DIR, "test", "masks")
    
    if not os.path.exists(test_dir_img):
        print(f"WARNING: Data directory {test_dir_img} not found.")
        return
        
    test_dataset = CivilCortexDataset(test_dir_img, test_dir_mask, transform=get_validation_augmentation())
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    # 3. Evaluation Metrics
    iou_scores = []
    dice_scores = []
    class_iou = {c: [] for c in range(CLASSES)}
    
    with torch.no_grad():
        for images, masks in test_loader:
            images = images.to(DEVICE)
            masks = masks.to(DEVICE)
            
            logits = model(images)
            preds = torch.argmax(logits, dim=1) # Shape: (B, H, W)
            
            # Calculate metrics per image
            for i in range(len(preds)):
                pred = preds[i]
                target = masks[i]
                
                # Exclude ignore_index (255) from evaluation
                valid_mask = (target != IGNORE_INDEX)
                
                pred_valid = pred[valid_mask]
                target_valid = target[valid_mask]
                
                if len(target_valid) == 0:
                    continue
                    
                # Calculate True Positives, False Positives, False Negatives per class
                tp, fp, fn, tn = smp.metrics.get_stats(
                    pred_valid.unsqueeze(0).unsqueeze(0), 
                    target_valid.unsqueeze(0).unsqueeze(0), 
                    mode='multiclass', 
                    num_classes=CLASSES
                )
                
                iou = smp.metrics.iou_score(tp, fp, fn, tn, reduction="micro")
                dice = smp.metrics.f1_score(tp, fp, fn, tn, reduction="micro")
                
                iou_scores.append(iou.item())
                dice_scores.append(dice.item())
                
                # Class-wise IoU
                class_iou_raw = smp.metrics.iou_score(tp, fp, fn, tn, reduction="none").squeeze()
                for c in range(CLASSES):
                    if c in target_valid: # Only count if class exists in ground truth
                        class_iou[c].append(class_iou_raw[c].item())
                        
    # 4. Report
    print("--------------------------------------------------")
    print("FINAL TEST METRICS")
    print("--------------------------------------------------")
    print(f"Mean Defect IoU: {np.mean(iou_scores):.4f}")
    print(f"Mean Defect Dice: {np.mean(dice_scores):.4f}")
    print(f"Background IoU: {np.mean(class_iou[0]):.4f}")
    print(f"Crack IoU: {np.mean(class_iou[1]):.4f}")
    print(f"Spalling IoU: {np.mean(class_iou[2]):.4f}")
    print(f"Corrosion IoU: {np.mean(class_iou[3]):.4f}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()
