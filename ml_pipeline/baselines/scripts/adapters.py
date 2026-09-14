import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageDraw
import torch
from torch.utils.data import Dataset
import torchvision.transforms.functional as TF

class SDNET2018Adapter(Dataset):
    def __init__(self, root_dir, transform=None, split="train", max_samples=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.samples = []
        
        for mat in ["D", "P", "W"]:
            for state in ["C", "U"]:
                cls_idx = 1 if state == "C" else 0
                dir_path = self.root_dir / mat / f"{state}{mat}"
                if dir_path.exists():
                    for img_path in dir_path.glob("*.jpg"):
                        self.samples.append((str(img_path), cls_idx))
                        if max_samples and len(self.samples) >= max_samples:
                            break
            if max_samples and len(self.samples) >= max_samples:
                break
                
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        else:
            image = TF.to_tensor(image)
        return image, label

class DamageDetectionAdapter(Dataset):
    def __init__(self, root_dir, transform=None, split="train", max_samples=None):
        self.root_dir = Path(root_dir) / "2750"
        self.transform = transform
        self.img_dir = self.root_dir / "img"
        self.annot_dir = self.root_dir / "annot"
        self.samples = []
        
        if self.annot_dir.exists():
            for xml_file in self.annot_dir.glob("*.xml"):
                img_path = self.img_dir / (xml_file.stem + ".jpg")
                if not img_path.exists():
                    img_path = self.img_dir / (xml_file.stem + ".png")
                if img_path.exists():
                    self.samples.append((str(img_path), str(xml_file)))
                    if max_samples and len(self.samples) >= max_samples:
                        break
                        
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        img_path, xml_path = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        boxes = []
        labels = []
        for obj in root.findall("object"):
            bndbox = obj.find("bndbox")
            xmin = float(bndbox.find("xmin").text)
            ymin = float(bndbox.find("ymin").text)
            xmax = float(bndbox.find("xmax").text)
            ymax = float(bndbox.find("ymax").text)
            boxes.append([xmin, ymin, xmax, ymax])
            labels.append(1) 
            
        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        if len(boxes) == 0:
            boxes = torch.empty((0, 4), dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)
        
        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        target["image_id"] = torch.tensor([idx])
        
        if self.transform:
            image = self.transform(image)
        else:
            image = TF.to_tensor(image)
            
        return image, target

class RC1841Adapter(Dataset):
    def __init__(self, root_dir, transform=None, split="train", max_samples=None):
        self.root_dir = Path(root_dir)
        self.img_dir = self.root_dir / "imagedata"
        self.label_dir = self.root_dir / "labeldata"
        self.transform = transform
        self.samples = []
        
        if self.label_dir.exists():
            for json_file in self.label_dir.glob("*.json"):
                img_path = self.img_dir / (json_file.stem + ".jpg")
                if not img_path.exists():
                    img_path = self.img_dir / (json_file.stem + ".png")
                if img_path.exists():
                    self.samples.append((str(img_path), str(json_file)))
                    if max_samples and len(self.samples) >= max_samples:
                        break
                        
    def __len__(self):
        return len(self.samples)
        
    def __getitem__(self, idx):
        img_path, json_path = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        
        with open(json_path, "r") as f:
            data = json.load(f)
            
        mask = Image.new("L", (image.width, image.height), 0)
        draw = ImageDraw.Draw(mask)
        
        for shape in data.get("shapes", []):
            if shape.get("shape_type") == "polygon":
                points = shape.get("points", [])
                if len(points) >= 3:
                    flattened = [tuple(p) for p in points]
                    draw.polygon(flattened, outline=1, fill=1)
                    
        if self.transform:
            image = self.transform(image)
            mask = mask.resize((image.shape[2], image.shape[1]), Image.NEAREST)
        else:
            image = TF.to_tensor(image)
            
        mask_tensor = torch.as_tensor(TF.to_tensor(mask).squeeze(0), dtype=torch.long)
        return image, mask_tensor
