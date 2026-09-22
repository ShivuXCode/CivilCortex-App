import segmentation_models_pytorch as smp

def create_model(arch="deeplabv3plus", backbone="efficientnet-b4", in_channels=3, classes=4):
    """
    Instantiates the CivilCortex semantic segmentation model.
    """
    if arch == "deeplabv3plus":
        return smp.DeepLabV3Plus(
            encoder_name=backbone,
            encoder_weights=None, # Loading trained weights manually
            in_channels=in_channels,
            classes=classes
        )
    raise ValueError(f"Architecture {arch} not supported.")
