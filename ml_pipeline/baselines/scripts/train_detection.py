import os
import time
import argparse
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2, FasterRCNN_ResNet50_FPN_V2_Weights
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from adapters import DamageDetectionAdapter

def collate_fn(batch):
    return tuple(zip(*batch))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, required=True)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--max_samples", type=int, default=50)
    args = parser.parse_args()
    
    print("============================================================")
    print("PIPELINE SMOKE TEST — NOT A PERFORMANCE BENCHMARK.")
    print("============================================================")
    
    # Force CPU for torchvision detection to prevent MPS hangs
    device = torch.device("cpu")
    print(f"Using device: {device}")
    
    dataset = DamageDetectionAdapter(args.data_dir, split="train", max_samples=args.max_samples)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn)
    
    weights = FasterRCNN_ResNet50_FPN_V2_Weights.DEFAULT
    model = fasterrcnn_resnet50_fpn_v2(weights=weights)
    num_classes = 2 # background + damage
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    model = model.to(device)
    
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)
    
    model.train()
    start_time = time.time()
    for epoch in range(args.epochs):
        running_loss = 0.0
        for i, (images, targets) in enumerate(dataloader):
            images = list(image.to(device) for image in images)
            
            # Remove empty box annotations to prevent NaN losses in torchvision 
            # if images have no objects during a smoke test.
            valid_targets = []
            for t in targets:
                valid_target = {}
                for k, v in t.items():
                    valid_target[k] = v.to(device)
                valid_targets.append(valid_target)

            optimizer.zero_grad()
            loss_dict = model(images, valid_targets)
            losses = sum(loss for loss in loss_dict.values())
            
            losses.backward()
            optimizer.step()
            
            running_loss += losses.item()
            
        print(f"Epoch [{epoch+1}/{args.epochs}], Loss: {running_loss/len(dataloader):.4f}")
        
    print(f"Smoke test completed in {time.time() - start_time:.2f} seconds.")
    print("PIPELINE SMOKE TEST — NOT A PERFORMANCE BENCHMARK.")

if __name__ == "__main__":
    main()
