import os
from pathlib import Path

def audit_sdnet(base_dir: Path):
    counts = {"CD": 0, "UD": 0, "CW": 0, "UW": 0, "CP": 0, "UP": 0}
    for struct in ["D", "W", "P"]:
        for crack_status in ["C", "U"]:
            subdir = base_dir / struct / f"{crack_status}{struct}"
            if subdir.exists():
                images = list(subdir.glob("*.jpg"))
                counts[f"{crack_status}{struct}"] = len(images)
    total = sum(counts.values())
    print(f"SDNET2018 Total: {total} | Breakdown: {counts}")

def audit_damage_detection(base_dir: Path):
    img_dir = base_dir / "2750" / "img"
    annot_dir = base_dir / "2750" / "annot"
    
    if img_dir.exists() and annot_dir.exists():
        imgs = list(img_dir.glob("*.jpg"))
        annots = list(annot_dir.glob("*.xml")) # usually Pascal VOC XML
        print(f"DAMAGE_DETECTION Total Images: {len(imgs)} | Annotations: {len(annots)}")
    else:
        print("DAMAGE_DETECTION: Directory missing or structured differently.")

def audit_rc1841(base_dir: Path):
    imagedata = base_dir / "imagedata"
    labeldata = base_dir / "labeldata"
    if imagedata.exists() and labeldata.exists():
        imgs = list(imagedata.glob("*.jpg")) + list(imagedata.glob("*.png"))
        masks = list(labeldata.glob("*.png"))
        print(f"RC1841 Total Images: {len(imgs)} | Masks: {len(masks)}")
    else:
        print("RC1841: Directory missing or structured differently.")

def main():
    staging = Path("Datasets_staging")
    print("--- DATASET AVAILABILITY AUDIT ---")
    if (staging / "SDNET2018").exists(): audit_sdnet(staging / "SDNET2018")
    if (staging / "DAMAGE_DETECTION_2750").exists(): audit_damage_detection(staging / "DAMAGE_DETECTION_2750")
    if (staging / "RC_SEGMENTATION_1841").exists(): audit_rc1841(staging / "RC_SEGMENTATION_1841")

if __name__ == "__main__":
    main()
