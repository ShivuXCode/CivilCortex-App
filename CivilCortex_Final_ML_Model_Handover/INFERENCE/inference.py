import os
import torch
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

from INFERENCE.model_definition import create_model
from INFERENCE.preprocessing import get_preprocessing

COLORS = {
    0: (0, 0, 0),          # Background (Black)
    1: (255, 0, 0),        # Crack (Red)
    2: (0, 255, 0),        # Spalling (Green)
    3: (0, 0, 255)         # Corrosion (Blue)
}

def load_civilcortex_model(checkpoint_path, device="cuda"):
    model = create_model()
    model.load_state_dict(torch.load(checkpoint_path, map_location=device, weights_only=True))
    model.to(device)
    model.eval()
    return model

def run_inference(image_path, model, device="cuda", resolution=384):
    image = np.array(Image.open(image_path).convert("RGB"))
    
    preprocess = get_preprocessing(resolution)
    tensor = preprocess(image=image)['image'].unsqueeze(0).to(device)
    
    with torch.no_grad():
        logits = model(tensor)
        # Logits -> Probabilities (Argmax)
        prediction = torch.argmax(logits, dim=1).squeeze(0).cpu().numpy()
        
    return image, prediction

def visualize_prediction(image, prediction, save_path):
    colored_mask = np.zeros((*prediction.shape, 3), dtype=np.uint8)
    for c, color in COLORS.items():
        colored_mask[prediction == c] = color
        
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(image)
    axes[0].set_title("Original Image")
    axes[0].axis("off")
    
    axes[1].imshow(colored_mask)
    axes[1].set_title("Predicted Defects")
    axes[1].axis("off")
    
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Saved visualization to {save_path}")

if __name__ == "__main__":
    print("Checking if model loads...")
    try:
        model = load_civilcortex_model("MODEL/Phase6_ArchDeepLabEff_best.pth", "cpu")
        print("SUCCESS: Model loaded correctly.")
    except Exception as e:
        print(f"FAILED: {e}")
