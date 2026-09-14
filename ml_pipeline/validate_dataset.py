"""
CivilCortex - Phase 2: Dataset Validator
Validates image datasets for binary crack classification before training.
"""

import os
import sys
import glob
import hashlib
from PIL import Image
import numpy as np

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

def compute_file_hash(filepath: str) -> str:
    """Computes SHA-256 hash of a file to detect exact duplicate images."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def validate_dataset(data_dir: str = "data"):
    print(f"=== CivilCortex Dataset Validation ===")
    print(f"Inspecting directory: {os.path.abspath(data_dir)}\n")

    if not os.path.exists(data_dir):
        print(f"[ERROR] Directory '{data_dir}' does not exist.")
        return False

    # Check for binary classification class folders
    class_names = ["no_crack", "crack"]
    folder_mapping = {
        "no_crack": ["no_crack", "non_crack", "no-crack", "negative", "0"],
        "crack": ["crack", "cracked", "positive", "1"]
    }

    found_folders = {}
    for target_class, variations in folder_mapping.items():
        for var in variations:
            candidate = os.path.join(data_dir, var)
            if os.path.isdir(candidate):
                found_folders[target_class] = candidate
                break

    if len(found_folders) < 2:
        print("[STATUS] Binary class folders ('crack' and 'no_crack') not found directly.")
        print("Searching all subdirectories for images...")
        all_images = []
        for ext in SUPPORTED_EXTENSIONS:
            all_images.extend(glob.glob(os.path.join(data_dir, f"**/*{ext}"), recursive=True))
            all_images.extend(glob.glob(os.path.join(data_dir, f"**/*{ext.upper()}"), recursive=True))
        
        if not all_images:
            print("\n" + "="*50)
            print("STATUS: BLOCKED — DATASET REQUIRED")
            print("No image files found in dataset directory.")
            print("Please provide a dataset organized as:")
            print(f"  {data_dir}/no_crack/*.jpg")
            print(f"  {data_dir}/crack/*.jpg")
            print("="*50 + "\n")
            return False
    
    # Analyze classes
    total_images = 0
    corrupt_files = []
    duplicate_hashes = {}
    duplicates = []
    resolutions = []
    class_counts = {}

    for cls_name, cls_path in found_folders.items():
        images = []
        for ext in SUPPORTED_EXTENSIONS:
            images.extend(glob.glob(os.path.join(cls_path, f"*{ext}")))
            images.extend(glob.glob(os.path.join(cls_path, f"*{ext.upper()}")))
        
        class_counts[cls_name] = len(images)
        total_images += len(images)
        print(f"Class '{cls_name}' ({cls_path}): {len(images)} images found.")

        for img_path in images:
            # 1. Check readability & corruption
            try:
                with Image.open(img_path) as img:
                    img.verify()
                with Image.open(img_path) as img:
                    w, h = img.size
                    resolutions.append((w, h))
                    if w < 32 or h < 32:
                        print(f"[WARNING] Suspiciously small image: {img_path} ({w}x{h})")
            except Exception as e:
                corrupt_files.append((img_path, str(e)))
                continue

            # 2. Check duplicates
            try:
                fhash = compute_file_hash(img_path)
                if fhash in duplicate_hashes:
                    duplicates.append((img_path, duplicate_hashes[fhash]))
                else:
                    duplicate_hashes[fhash] = img_path
            except Exception:
                pass

    print("\n--- Validation Summary ---")
    print(f"Total images found: {total_images}")
    for cls, count in class_counts.items():
        print(f"  {cls}: {count}")

    if total_images == 0:
        print("\nSTATUS: BLOCKED — DATASET REQUIRED")
        return False

    print(f"Corrupt / Unreadable files: {len(corrupt_files)}")
    if corrupt_files:
        for f, err in corrupt_files[:5]:
            print(f"  Corrupt: {f} ({err})")

    print(f"Exact Duplicate files: {len(duplicates)}")
    if duplicates:
        for f1, f2 in duplicates[:5]:
            print(f"  Duplicate: {f1} == {f2}")

    if resolutions:
        widths, heights = zip(*resolutions)
        print(f"Resolution range: Min ({min(widths)}x{min(heights)}) to Max ({max(widths)}x{max(heights)})")
        print(f"Median resolution: {int(np.median(widths))}x{int(np.median(heights))}")

    # Check class balance
    if len(class_counts) == 2:
        c1, c2 = list(class_counts.values())
        ratio = max(c1, c2) / (min(c1, c2) + 1e-6)
        print(f"Class imbalance ratio: {ratio:.2f}:1")
        if ratio > 3.0:
            print("[WARNING] Significant class imbalance detected (>3:1). Consider class weighting.")

    print("\nDataset validation complete.")
    return True

if __name__ == "__main__":
    dir_to_check = sys.argv[1] if len(sys.argv) > 1 else "data"
    validate_dataset(dir_to_check)
