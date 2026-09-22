import albumentations as A
from albumentations.pytorch import ToTensorV2

def get_preprocessing(resolution=384):
    """
    Returns the exact preprocessing pipeline used during training.
    """
    return A.Compose([
        A.Resize(resolution, resolution),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2()
    ])
