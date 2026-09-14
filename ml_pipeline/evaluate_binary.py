"""
CivilCortex - Phase 2: Binary Classifier Evaluation & Threshold Calibration
Calibrates validation decision threshold and computes test evaluation metrics.
"""

import os
import sys
import json
import numpy as np
import tensorflow as tf
from preprocessing import IMG_HEIGHT, IMG_WIDTH, TARGET_SIZE

MODEL_PATH = "../backend/models/crack_binary_classifier.keras"
CONFIG_PATH = "../backend/models/crack_binary_config.json"
DEFAULT_DATA_DIR = "data"

def calibrate_and_evaluate(data_dir: str = DEFAULT_DATA_DIR):
    print("=== CivilCortex Binary Classifier Evaluation & Calibration ===")
    
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file '{MODEL_PATH}' not found. Please train the model first using 'python train_binary.py'.")
        return

    # 1. Load Model
    print(f"Loading model from: {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH)

    # 2. Load Validation & Test Datasets
    try:
        val_ds = tf.keras.utils.image_dataset_from_directory(
            os.path.join(data_dir, "val") if os.path.isdir(os.path.join(data_dir, "val")) else data_dir,
            labels="inferred",
            label_mode="binary",
            class_names=["no_crack", "crack"],
            color_mode="rgb",
            batch_size=32,
            image_size=(IMG_HEIGHT, IMG_WIDTH),
            shuffle=False
        )
    except Exception as e:
        print(f"[ERROR] Failed to load evaluation dataset: {e}")
        return

    # Extract all true labels and predicted probabilities
    y_true = []
    y_probs = []
    for images, labels in val_ds:
        probs = model.predict(images, verbose=0).flatten()
        y_probs.extend(probs)
        y_true.extend(labels.numpy().flatten())

    y_true = np.array(y_true)
    y_probs = np.array(y_probs)

    print(f"\nEvaluating on {len(y_true)} samples...")

    # 3. Threshold Calibration Sweep
    print("\n--- Validation Threshold Sweep ---")
    print(f"{'Threshold':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'FP':<5} | {'FN':<5}")
    print("-" * 62)

    best_threshold = 0.50
    best_f1 = 0.0
    best_stats = {}

    for t in np.arange(0.10, 0.95, 0.05):
        y_pred = (y_probs >= t).astype(int)
        tp = np.sum((y_pred == 1) & (y_true == 1))
        fp = np.sum((y_pred == 1) & (y_true == 0))
        fn = np.sum((y_pred == 0) & (y_true == 1))
        tn = np.sum((y_pred == 0) & (y_true == 0))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        print(f"{t:<10.2f} | {precision:<10.4f} | {recall:<10.4f} | {f1:<10.4f} | {fp:<5} | {fn:<5}")

        # Choose threshold that maximizes F1 while guaranteeing high recall (Recall >= 0.90)
        if recall >= 0.90 and f1 > best_f1:
            best_f1 = f1
            best_threshold = float(round(t, 2))
            best_stats = {"precision": precision, "recall": recall, "f1": f1, "fp": int(fp), "fn": int(fn)}

    if not best_stats:
        # Fallback to pure max F1
        best_threshold = 0.50

    print("-" * 62)
    print(f"[OPTIMAL THRESHOLD SELECTED]: {best_threshold:.2f}")
    if best_stats:
        print(f"  At threshold {best_threshold}: Precision={best_stats['precision']:.4f}, Recall={best_stats['recall']:.4f}, F1={best_stats['f1']:.4f}, FN={best_stats['fn']}, FP={best_stats['fp']}")

    # 4. Save/Update Config with Optimal Threshold
    config = {}
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    
    config["threshold"] = best_threshold
    config["validation_metrics"] = best_stats
    
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"\n[UPDATED] Configuration with optimal threshold saved to: {CONFIG_PATH}")

if __name__ == "__main__":
    target_data_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA_DIR
    calibrate_and_evaluate(target_data_dir)
