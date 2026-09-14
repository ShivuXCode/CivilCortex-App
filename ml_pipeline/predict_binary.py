"""
CivilCortex - Phase 2: Binary Crack Prediction Script
Standalone prediction utility for single image inference using the new binary classifier.
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf
from preprocessing import preprocess_for_inference

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "models", "crack_binary_classifier.keras")
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "models", "crack_binary_config.json")

def predict_single_image(image_path: str):
    if not os.path.exists(image_path):
        print(f"[ERROR] Image path '{image_path}' does not exist.")
        sys.exit(1)

    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file '{MODEL_PATH}' not found.")
        print("Please train the model first using 'python train_binary.py'.")
        sys.exit(1)

    # 1. Load Configuration & Threshold
    threshold = 0.50
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                cfg = json.load(f)
                threshold = float(cfg.get("threshold", 0.50))
        except Exception:
            pass

    # 2. Load Model
    model = tf.keras.models.load_model(MODEL_PATH)

    # 3. Preprocess Image (Using standardized shared pipeline)
    tensor = preprocess_for_inference(image_path)

    # 4. Predict
    pred_prob = float(model.predict(tensor, verbose=0)[0][0])

    # 5. Apply Threshold
    prediction = "CRACK" if pred_prob >= threshold else "NO_CRACK"

    # 6. Format Output
    print(f"Image: {os.path.basename(image_path)}")
    print(f"Prediction: {prediction}")
    print(f"Probability: {pred_prob:.4f}")
    print(f"Threshold: {threshold:.2f}")

    return {
        "image": image_path,
        "prediction": prediction,
        "probability": pred_prob,
        "threshold": threshold
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict_binary.py <path_to_image>")
        sys.exit(1)
    predict_single_image(sys.argv[1])
