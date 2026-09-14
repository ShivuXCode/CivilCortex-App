"""
CivilCortex - Phase 2: Binary Crack Classifier Training Pipeline
Trains an EfficientNetB0 image-level binary classifier using 2-stage transfer learning.
"""

import os
import sys
import json
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from preprocessing import IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS, get_augmentation_layer

# Set reproducible seeds
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# Hyperparameters
BATCH_SIZE = 32
STAGE1_EPOCHS = 15
STAGE2_EPOCHS = 25
STAGE1_LR = 1e-3
STAGE2_LR = 1e-5
DEFAULT_DATA_DIR = "data"
MODEL_SAVE_PATH = "../backend/models/crack_binary_classifier.keras"
CONFIG_SAVE_PATH = "../backend/models/crack_binary_config.json"

def build_binary_classifier():
    """
    Builds an EfficientNetB0 binary classification model:
    Input (224, 224, 3) -> Augmentation (training only) -> EfficientNetB0 (ImageNet) -> GAP -> Dropout(0.3) -> Dense(1, Sigmoid)
    """
    inputs = layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, IMG_CHANNELS), name="input_image")
    
    # 1. Training Augmentation
    aug = get_augmentation_layer()(inputs)
    
    # 2. Pretrained EfficientNetB0 Backbone (Pretrained on ImageNet)
    # Note: EfficientNet has built-in Rescaling if inputs are [0, 255]
    backbone = tf.keras.applications.EfficientNetB0(
        include_top=False,
        weights="imagenet",
        input_tensor=aug
    )
    
    # Freeze backbone for Stage 1
    backbone.trainable = False
    
    # 3. Classification Head
    x = layers.GlobalAveragePooling2D(name="global_avg_pool")(backbone.output)
    x = layers.Dropout(0.3, name="top_dropout")(x)
    outputs = layers.Dense(1, activation="sigmoid", name="crack_probability")(x)
    
    model = models.Model(inputs=inputs, outputs=outputs, name="civilcortex_binary_crack_classifier")
    return model, backbone

def create_datasets(data_dir: str, val_split: float = 0.15, test_split: float = 0.15):
    """
    Creates deterministic Train / Validation / Test dataset splits from directory.
    Expected folder structure:
      data_dir/
        no_crack/
        crack/
    """
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory '{data_dir}' not found.")

    # Load complete dataset
    full_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        labels="inferred",
        label_mode="binary",
        class_names=["no_crack", "crack"], # 0 = no_crack, 1 = crack
        color_mode="rgb",
        batch_size=BATCH_SIZE,
        image_size=(IMG_HEIGHT, IMG_WIDTH),
        shuffle=True,
        seed=SEED
    )
    
    num_batches = len(full_ds)
    if num_batches == 0:
        raise ValueError("Dataset is empty.")

    val_batches = max(1, int(num_batches * val_split))
    test_batches = max(1, int(num_batches * test_split))
    train_batches = num_batches - val_batches - test_batches

    print(f"Total Batches: {num_batches} | Train: {train_batches} | Val: {val_batches} | Test: {test_batches}")

    train_ds = full_ds.take(train_batches)
    remaining = full_ds.skip(train_batches)
    val_ds = remaining.take(val_batches)
    test_ds = remaining.skip(val_batches)

    # Prefetch for performance
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
    test_ds = test_ds.cache().prefetch(buffer_size=AUTOTUNE)

    return train_ds, val_ds, test_ds

def train_pipeline(data_dir: str = DEFAULT_DATA_DIR):
    print("=== CivilCortex Phase 2: Binary Classifier Training ===")
    
    # 1. Prepare Datasets
    try:
        train_ds, val_ds, test_ds = create_datasets(data_dir)
    except Exception as e:
        print(f"\n[ERROR] Failed to load dataset: {e}")
        print("Please ensure dataset is placed in 'ml_pipeline/data/' with 'no_crack/' and 'crack/' folders.")
        return

    # 2. Build Model
    model, backbone = build_binary_classifier()
    
    # 3. Stage 1: Feature Extraction (Backbone Frozen)
    print("\n--- Stage 1: Training Classification Head ---")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE1_LR),
        loss=tf.keras.losses.BinaryCrossentropy(label_smoothing=0.05),
        metrics=[
            "accuracy",
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.AUC(curve="PR", name="pr_auc")
        ]
    )
    
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
    
    stage1_callbacks = [
        callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True, verbose=1),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-6, verbose=1)
    ]
    
    history1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE1_EPOCHS,
        callbacks=stage1_callbacks
    )
    
    # 4. Stage 2: Fine-Tuning (Unfreeze top layers of Backbone)
    print("\n--- Stage 2: Fine-Tuning Upper Backbone Layers ---")
    backbone.trainable = True
    # Freeze the first 100 layers and fine-tune top layers
    for layer in backbone.layers[:100]:
        layer.trainable = False
        
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=STAGE2_LR),
        loss=tf.keras.losses.BinaryCrossentropy(label_smoothing=0.05),
        metrics=[
            "accuracy",
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
            tf.keras.metrics.AUC(name="auc"),
            tf.keras.metrics.AUC(curve="PR", name="pr_auc")
        ]
    )
    
    stage2_callbacks = [
        callbacks.EarlyStopping(monitor="val_loss", patience=6, restore_best_weights=True, verbose=1),
        callbacks.ModelCheckpoint(MODEL_SAVE_PATH, monitor="val_recall", mode="max", save_best_only=True, verbose=1),
        callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.3, patience=2, min_lr=1e-7, verbose=1)
    ]
    
    history2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE2_EPOCHS,
        callbacks=stage2_callbacks
    )
    
    # Save final model
    model.save(MODEL_SAVE_PATH)
    print(f"\n[SUCCESS] Model successfully saved to: {MODEL_SAVE_PATH}")
    
    # Initialize basic config (threshold will be calibrated by evaluate_binary.py)
    config = {
        "task": "binary_classification",
        "class_names": ["no_crack", "crack"],
        "input_size": [IMG_HEIGHT, IMG_WIDTH],
        "color_mode": "RGB",
        "dtype": "float32",
        "model_architecture": "EfficientNetB0",
        "threshold": 0.50,
        "framework": "TensorFlow/Keras",
        "seed": SEED
    }
    with open(CONFIG_SAVE_PATH, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Configuration template saved to: {CONFIG_SAVE_PATH}")
    print("\nNext step: Run 'python evaluate_binary.py' to calibrate validation threshold and test performance.")

if __name__ == "__main__":
    target_data_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DATA_DIR
    train_pipeline(target_data_dir)
