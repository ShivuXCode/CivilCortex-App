import os
import time
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision.models.segmentation import fcn_resnet50, FCN_ResNet50_Weights
from adapters import RC1841Adapter
import torchvision.transforms as transforms

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, required=True)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--max_samples", type=int, default=30)
    args = parser.parse_args()
    
    print("============================================================")
    print("PIPELINE SMOKE TEST — NOT A PERFORMANCE BENCHMARK.")
    print("============================================================")
    
    device = torch.device("mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu"))
    print(f"Using device: {device}")
    
    # Very simple transform for smoke test: resize image and tensorize.
    # The adapter handles resizing mask.
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    dataset = RC1841Adapter(args.data_dir, transform=transform, split="train", max_samples=args.max_samples)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    
    model = fcn_resnet50(weights=FCN_ResNet50_Weights.DEFAULT)
    # Change number of classes to 2 (background + crack)
    model.classifier[4] = nn.Conv2d(512, 2, kernel_size=(1, 1), stride=(1, 1))
    model.aux_classifier[4] = nn.Conv2d(256, 2, kernel_size=(1, 1), stride=(1, 1))
    
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    
    model.train()
    start_time = time.time()
    for epoch in range(args.epochs):
        running_loss = 0.0
        for i, (inputs, masks) in enumerate(dataloader):
            inputs = inputs.to(device)
            masks = masks.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)["out"]
            loss = criterion(outputs, masks)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        print(f"Epoch [{epoch+1}/{args.epochs}], Loss: {running_loss/len(dataloader):.4f}")
        
    print(f"Smoke test completed in {time.time() - start_time:.2f} seconds.")
    print("PIPELINE SMOKE TEST — NOT A PERFORMANCE BENCHMARK.")

if __name__ == "__main__":
    main()
