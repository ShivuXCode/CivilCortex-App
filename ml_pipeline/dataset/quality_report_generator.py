import json
from collections import Counter
from pathlib import Path
from metadata_schema import ImageMetadata

def generate_quality_report(metadata_dir: str):
    p = Path(metadata_dir)
    
    report = {
        "total_images": 0,
        "total_defect_instances": 0,
        "defect_type_distribution": Counter(),
        "morphology_distribution": Counter(),
        "image_resolution_distribution": Counter(),
        "quality_failures": 0,
        "calibration_availability": {"calibrated": 0, "uncalibrated": 0},
        "unique_sites": set()
    }
    
    if p.exists():
        for json_file in p.glob("*.json"):
            with open(json_file, 'r') as f:
                data = json.load(f)
                img = ImageMetadata(**data)
                
                report["total_images"] += 1
                
                # Tracking unique sites by combining building_id and site_id if available
                site_key = f"{img.building_id or ''}_{img.site_id or ''}"
                if site_key != "_":
                    report["unique_sites"].add(site_key)
                
                res_key = f"{img.image_width}x{img.image_height}"
                report["image_resolution_distribution"][res_key] += 1
                
                if img.quality_status != "PASS":
                    report["quality_failures"] += 1
                
                if img.calibration.is_calibrated:
                    report["calibration_availability"]["calibrated"] += 1
                else:
                    report["calibration_availability"]["uncalibrated"] += 1
                    
                for defect in img.defects:
                    report["total_defect_instances"] += 1
                    report["defect_type_distribution"][defect.defect_type] += 1
                    for morph in defect.morphology_labels:
                        report["morphology_distribution"][morph] += 1

    # Convert sets/counters for JSON serialization
    report["unique_sites_count"] = len(report["unique_sites"])
    del report["unique_sites"]
    report["defect_type_distribution"] = dict(report["defect_type_distribution"])
    report["morphology_distribution"] = dict(report["morphology_distribution"])
    report["image_resolution_distribution"] = dict(report["image_resolution_distribution"])
    
    out_dir = p.parent / "quality_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "dataset_quality_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    return report

if __name__ == "__main__":
    generate_quality_report("metadata")
