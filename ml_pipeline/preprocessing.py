"""
CivilCortex - Phase 2: Binary Crack Classifier Preprocessing Pipeline
Standardized preprocessing shared identically across training, validation, testing, and inference.
"""

import numpy as np
import tensorflow as tf
from PIL import Image
import io
from typing import Tuple, Union

# Standard Model Input Configuration
IMG_HEIGHT = 224
IMG_WIDTH = 224
IMG_CHANNELS = 3
TARGET_SIZE: Tuple[int, int] = (IMG_WIDTH, IMG_HEIGHT)
DTYPE = tf.float32

def load_and_preprocess_image(
    image_input: Union[str, bytes, Image.Image],
    target_size: Tuple[int, int] = TARGET_SIZE
) -> np.ndarray:
    """
    Standardized Image Preprocessing:
    1. Loads image from file path, raw bytes, or PIL Image.
    2. Converts strictly to RGB (3 channels, standard RGB ordering).
    3. Resizes to target resolution (224x224) using bilinear interpolation.
    4. Converts to float32 normalized array in [0.0, 255.0] (matching EfficientNetB0 standard preprocessing).
    
    Returns:
        np.ndarray of shape (224, 224, 3) and dtype float32.
    """
    if isinstance(image_input, str):
        img = Image.open(image_input)
    elif isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input))
    elif isinstance(image_input, Image.Image):
        img = image_input
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    # Ensure RGB color space (discards alpha, converts grayscale to 3-channel RGB)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Resize to target dimension
    img = img.resize(target_size, Image.Resampling.BILINEAR)

    # Convert to float32 numpy array
    img_array = np.array(img, dtype=np.float32)

    return img_array

def preprocess_for_inference(
    image_input: Union[str, bytes, Image.Image],
    target_size: Tuple[int, int] = TARGET_SIZE
) -> np.ndarray:
    """
    Preprocesses a single image and adds the batch dimension for model inference.
    Returns:
        np.ndarray of shape (1, 224, 224, 3) and dtype float32.
    """
    img_array = load_and_preprocess_image(image_input, target_size=target_size)
    return np.expand_dims(img_array, axis=0)

def get_augmentation_layer():
    """
    Returns Keras Sequential augmentation layer applied ONLY during training.
    """
    return tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.1), # +/- 36 degrees
        tf.keras.layers.RandomTranslation(0.05, 0.05),
        tf.keras.layers.RandomZoom(0.05),
        tf.keras.layers.RandomContrast(0.1),
    ], name="data_augmentation")
