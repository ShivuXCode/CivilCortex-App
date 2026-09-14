import os
import glob
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import cv2

# Configuration
IMG_WIDTH = 256
IMG_HEIGHT = 256
BATCH_SIZE = 8
EPOCHS = 20
DATA_DIR = "data"
MODEL_SAVE_PATH = "../backend/models/civilcortex_best_v2.keras"

def get_unet_model(img_width, img_height, num_classes=1):
    """
    Builds a standard U-Net architecture for semantic segmentation of cracks.
    """
    inputs = layers.Input((img_height, img_width, 3))

    # Encoder
    c1 = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(inputs)
    c1 = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(c1)
    p1 = layers.MaxPooling2D((2, 2))(c1)

    c2 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(p1)
    c2 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c2)
    p2 = layers.MaxPooling2D((2, 2))(c2)

    c3 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(p2)
    c3 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c3)
    p3 = layers.MaxPooling2D((2, 2))(c3)

    # Bottleneck
    c4 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(p3)
    c4 = layers.Conv2D(256, (3, 3), activation='relu', padding='same')(c4)

    # Decoder
    u5 = layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(c4)
    u5 = layers.concatenate([u5, c3])
    c5 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(u5)
    c5 = layers.Conv2D(128, (3, 3), activation='relu', padding='same')(c5)

    u6 = layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(c5)
    u6 = layers.concatenate([u6, c2])
    c6 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(u6)
    c6 = layers.Conv2D(64, (3, 3), activation='relu', padding='same')(c6)

    u7 = layers.Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same')(c6)
    u7 = layers.concatenate([u7, c1])
    c7 = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(u7)
    c7 = layers.Conv2D(32, (3, 3), activation='relu', padding='same')(c7)

    # Output Layer
    outputs = layers.Conv2D(num_classes, (1, 1), activation='sigmoid')(c7)

    model = models.Model(inputs=[inputs], outputs=[outputs])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def load_data():
    """
    Loads images and binary masks from the local filesystem.
    Make sure masks are named identically to their corresponding images.
    """
    image_paths = sorted(glob.glob(os.path.join(DATA_DIR, "images", "*.jpg")))
    mask_paths = sorted(glob.glob(os.path.join(DATA_DIR, "masks", "*.jpg")))

    if not image_paths or not mask_paths:
        print("No training data found in ml_pipeline/data/images/ and ml_pipeline/data/masks/")
        print("Please add .jpg images and masks before running.")
        return None, None

    X, Y = [], []
    for img_path, mask_path in zip(image_paths, mask_paths):
        # Load and resize image
        img = cv2.imread(img_path)
        img = cv2.resize(img, (IMG_WIDTH, IMG_HEIGHT))
        img = img / 255.0  # Normalize

        # Load and resize mask (grayscale)
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        mask = cv2.resize(mask, (IMG_WIDTH, IMG_HEIGHT))
        mask = mask / 255.0  # Normalize to 0-1
        mask = np.expand_dims(mask, axis=-1)

        X.append(img)
        Y.append(mask)

    return np.array(X), np.array(Y)

if __name__ == "__main__":
    print("Initializing CivilCortex Vision Retraining Pipeline...")
    X_train, Y_train = load_data()
    
    if X_train is not None:
        print(f"Loaded {len(X_train)} samples.")
        model = get_unet_model(IMG_WIDTH, IMG_HEIGHT)
        print("Model architecture built. Starting training...")
        
        # Train model
        model.fit(X_train, Y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, validation_split=0.2)
        
        # Save model directly to backend folder for immediate use
        model.save(MODEL_SAVE_PATH)
        print(f"Model successfully saved to: {MODEL_SAVE_PATH}")
        print("To use the new model, update agent1_condition.py to load civilcortex_best_v2.keras")
