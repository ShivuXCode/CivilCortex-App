import os
import glob
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image
import imagehash
from tqdm import tqdm

DATASETS_ROOT = "/Users/shivanisrimurugesan/civilcortex_project/Datasets_staging"
OUTPUT_FILE = "/Users/shivanisrimurugesan/civilcortex_project/ml_pipeline/dataset/quality_reports/duplicate_clusters.json"

# Tunable thresholds for pHash
EXACT_MATCH_THRESHOLD = 0
LIKELY_DUPLICATE_THRESHOLD = 4
LIKELY_SAME_SCENE_THRESHOLD = 8
POSSIBLE_SAME_PHYSICAL_DEFECT = 12

def process_image(img_path):
    try:
        with Image.open(img_path) as img:
            # Calculate pHash
            hash_val = imagehash.phash(img)
            # We convert it to a string for JSON serialization
            return img_path, str(hash_val), None
    except Exception as e:
        return img_path, None, str(e)

def compute_hashes(image_paths, num_workers=None):
    results = {}
    errors = {}
    print(f"Computing perceptual hashes for {len(image_paths)} images...")
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_image, path): path for path in image_paths}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Hashing"):
            img_path, h_val, err = future.result()
            if err:
                errors[img_path] = err
            else:
                results[img_path] = h_val
                
    return results, errors

def analyze_duplicates(hashes_dict):
    # hashes_dict: {path: hash_string}
    # To compare efficiently, group by exact hashes first
    exact_clusters = {}
    for path, h_str in hashes_dict.items():
        exact_clusters.setdefault(h_str, []).append(path)
        
    unique_hashes = list(exact_clusters.keys())
    
    # We will build clusters of near duplicates
    near_clusters = []
    
    # Pre-parse hash strings to 64-bit integers for blazing fast bitwise comparison
    parsed_hashes = {h_str: int(h_str, 16) for h_str in unique_hashes}
    
    # Naive O(N^2) comparison on unique hashes (which should be fewer)
    n = len(unique_hashes)
    print(f"Comparing {n} unique hashes (approx {n*(n-1)//2} comparisons)...")
    
    # To group them, we use a basic connected components approach
    # We'll build an adjacency list
    adj = {h: [] for h in unique_hashes}
    
    # Keep track of counts for reporting
    exact_duplicate_count = sum(len(paths) - 1 for paths in exact_clusters.values())
    cross_dataset_exact = 0
    within_dataset_exact = 0
    
    for paths in exact_clusters.values():
        if len(paths) > 1:
            datasets = set(p.split('/Datasets_staging/')[1].split('/')[0] for p in paths)
            if len(datasets) > 1:
                cross_dataset_exact += len(paths) - 1
            else:
                within_dataset_exact += len(paths) - 1

    # Perform comparisons using fast bitwise XOR
    for i in tqdm(range(n), desc="Comparing unique hashes", mininterval=1.0):
        h1 = unique_hashes[i]
        int1 = parsed_hashes[h1]
        for j in range(i + 1, n):
            h2 = unique_hashes[j]
            int2 = parsed_hashes[h2]
            
            distance = (int1 ^ int2).bit_count()
            if distance <= POSSIBLE_SAME_PHYSICAL_DEFECT:
                adj[h1].append((h2, distance))
                adj[h2].append((h1, distance))

    # Find connected components (clusters)
    visited = set()
    clusters_out = []
    cluster_id_counter = 1
    
    for h in unique_hashes:
        if h not in visited:
            # BFS or DFS to find component
            component = []
            q = [h]
            visited.add(h)
            
            while q:
                curr = q.pop(0)
                component.append(curr)
                for neighbor, dist in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
            
            # Form cluster report
            if len(component) > 1 or len(exact_clusters[component[0]]) > 1:
                # This component has >1 image
                # Let's collect all paths
                cluster_images = []
                for ch in component:
                    cluster_images.extend(exact_clusters[ch])
                
                # Determine type
                datasets = set(p.split('/Datasets_staging/')[1].split('/')[0] for p in cluster_images)
                
                # We can calculate max distance within the component
                max_dist = 0
                for i_c in range(len(component)):
                    for j_c in range(i_c+1, len(component)):
                        d = parsed_hashes[component[i_c]] - parsed_hashes[component[j_c]]
                        if d > max_dist: max_dist = d
                
                if max_dist == 0:
                    dup_type = "EXACT_DUPLICATE"
                    rec_action = "KEEP_ONE_REPRESENTATIVE"
                elif max_dist <= LIKELY_DUPLICATE_THRESHOLD:
                    dup_type = "LIKELY_DUPLICATE"
                    rec_action = "KEEP_ONE_REPRESENTATIVE_OR_REVIEW"
                elif max_dist <= LIKELY_SAME_SCENE_THRESHOLD:
                    dup_type = "LIKELY_SAME_SCENE"
                    rec_action = "ENSURE_SAME_SPLIT"
                else:
                    dup_type = "POSSIBLE_SAME_PHYSICAL_DEFECT"
                    rec_action = "HUMAN_REVIEW_RECOMMENDED"
                    
                clusters_out.append({
                    "cluster_id": f"CLUST_{cluster_id_counter:05d}",
                    "image_count": len(cluster_images),
                    "datasets": list(datasets),
                    "cross_dataset": len(datasets) > 1,
                    "max_phash_distance": max_dist,
                    "duplicate_type": dup_type,
                    "recommended_action": rec_action,
                    "image_paths": cluster_images
                })
                cluster_id_counter += 1

    return {
        "metrics": {
            "total_images_processed": len(hashes_dict),
            "exact_duplicate_count": exact_duplicate_count,
            "within_dataset_exact": within_dataset_exact,
            "cross_dataset_exact": cross_dataset_exact,
            "near_duplicate_cluster_count": len(clusters_out),
            "total_unique_hashes": len(unique_hashes)
        },
        "clusters": clusters_out
    }

def main():
    start_time = time.time()
    
    # 1. Collect all images
    print(f"Scanning {DATASETS_ROOT} for images...")
    image_paths = []
    extensions = ('*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp')
    for root, dirs, files in os.walk(DATASETS_ROOT):
        for ext in extensions:
            image_paths.extend(glob.glob(os.path.join(root, ext)))
            image_paths.extend(glob.glob(os.path.join(root, ext.upper())))
            
    # Deduplicate paths just in case
    image_paths = list(set(image_paths))
    print(f"Found {len(image_paths)} images.")
    
    # 2. Compute hashes
    # Check cache first
    cache_path = os.path.join(os.path.dirname(OUTPUT_FILE), "phash_cache.json")
    if os.path.exists(cache_path):
        print("Loading cached hashes...")
        with open(cache_path, "r") as f:
            data = json.load(f)
            hashes = data.get("hashes", {})
            errors = data.get("errors", {})
    else:
        hashes, errors = compute_hashes(image_paths, num_workers=os.cpu_count() or 4)
        print(f"Saving {len(hashes)} hashes to cache...")
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump({"hashes": hashes, "errors": errors}, f)
            
    print(f"Successfully hashed {len(hashes)} images. Errors: {len(errors)}")
    
    # 3. Analyze duplicates
    analysis_result = analyze_duplicates(hashes)
    
    # 4. Save result
    analysis_result["processing_stats"] = {
        "runtime_seconds": time.time() - start_time,
        "failed_files": len(errors),
        "thresholds": {
            "exact": EXACT_MATCH_THRESHOLD,
            "likely_duplicate": LIKELY_DUPLICATE_THRESHOLD,
            "likely_same_scene": LIKELY_SAME_SCENE_THRESHOLD,
            "possible_same_physical_defect": POSSIBLE_SAME_PHYSICAL_DEFECT,
            "reasoning": "pHash distance 0 is exact exact duplicate (or trivially resized). <=4 indicates minor compression/watermark changes. <=8 indicates likely identical scene (different crop/lighting). <=12 is borderline similar texture/defect which requires manual verification."
        }
    }
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(analysis_result, f, indent=4)
        
    print(f"Duplicate analysis complete. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
