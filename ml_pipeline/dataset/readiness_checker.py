import json
from pathlib import Path
from typing import Dict, Any

class FieldDataReadinessChecker:
    def __init__(self, target_matrix_path: Path):
        with open(target_matrix_path, "r") as f:
            self.targets = json.load(f)
            
        self._validate_mathematical_consistency()
            
    def _validate_mathematical_consistency(self):
        target_res = self.targets.get("target_resolution", {})
        if target_res.get("status") == "APPROVED" and target_res.get("approved_option"):
            active_target = target_res["options"][target_res["approved_option"]]
        else:
            active_target = self.targets.get("acceptance_gate", {})
            
        dt_dist = active_target.get("defect_type_distribution", {})
        crack_min = dt_dist.get("crack", {}).get("minimum_instances", 0)
        spalling_min = dt_dist.get("spalling", {}).get("minimum_instances", 0)
        efflorescence_min = dt_dist.get("efflorescence", {}).get("minimum_instances", 0)
        
        total_class_min = crack_min + spalling_min + efflorescence_min
        min_instances = active_target.get("minimum_defect_instances", 0)
        
        if total_class_min > min_instances:
            raise ValueError(f"Mathematically inconsistent targets: class minimums ({total_class_min}) exceed total minimum ({min_instances}).")
            
    def check_readiness(self, metadata_dir: Path) -> Dict[str, Any]:
        report = {
            "sites": set(),
            "defect_instances": set(),
            "images": 0,
            "crack_instances": 0,
            "spalling_instances": 0,
            "efflorescence_instances": 0,
            "hard_negatives": 0,
            "morphology_coverage": {
                "horizontal": 0, "vertical": 0, "diagonal": 0, "branching": 0, "irregular": 0
            },
            "calibrated_observations": 0,
            "status": "FAIL",
            "blockers": []
        }
        
        target_res = self.targets.get("target_resolution", {})
        if target_res.get("status") == "PENDING_FORMAL_APPROVAL":
            report["status"] = "BLOCKED"
            report["blockers"].append("FIELD TARGET RESOLUTION: BLOCKED. Reason: 2,000 vs 3,100 physical-defect target has not been formally resolved.")
            return report
            
        if not metadata_dir.exists():
            report["blockers"].append("Metadata directory does not exist.")
            return report
            
        for json_file in metadata_dir.glob("*.json"):
            with open(json_file, "r") as f:
                data = json.load(f)
                
            # Do not count test fixtures, synthetics, or public datasets.
            # In a real environment, this might check specific provenance fields.
            # For now, we trust files in the field metadata dir.
            report["images"] += 1
            report["sites"].add(data.get("site_id"))
            
            calib = data.get("calibration", {}).get("status")
            if calib == "PHYSICAL_CALIBRATED":
                report["calibrated_observations"] += 1
                
            for defect in data.get("defects", []):
                inst_id = defect.get("defect_instance_id")
                report["defect_instances"].add(inst_id)
                dtype = defect.get("defect_type")
                
                if dtype == "crack":
                    report["crack_instances"] += 1
                    for morph in defect.get("morphology_tags", []):
                        if morph in report["morphology_coverage"]:
                             report["morphology_coverage"][morph] += 1
                elif dtype == "spalling":
                    report["spalling_instances"] += 1
                elif dtype == "efflorescence":
                    report["efflorescence_instances"] += 1
                elif dtype == "hard_negative":
                    report["hard_negatives"] += 1
                    
        # Evaluate against targets
        if target_res.get("status") == "APPROVED" and target_res.get("approved_option"):
            active_target = target_res["options"][target_res["approved_option"]]
        else:
            active_target = self.targets.get("acceptance_gate", {})
            
        gate = self.targets.get("acceptance_gate", {})
        min_instances = active_target.get("minimum_defect_instances", 2000)
        min_sites = gate.get("minimum_distinct_sites", 10)
        
        if len(report["defect_instances"]) < min_instances:
            report["blockers"].append(f"Insufficient defect instances. Found {len(report['defect_instances'])}, need {min_instances}")
        if len(report["sites"]) < min_sites:
            report["blockers"].append(f"Insufficient distinct sites. Found {len(report['sites'])}, need {min_sites}")
            
        dt_dist = active_target.get("defect_type_distribution", {})
        if report["crack_instances"] < dt_dist.get("crack", {}).get("minimum_instances", 1500):
            report["blockers"].append("Insufficient crack instances.")
        if report["spalling_instances"] < dt_dist.get("spalling", {}).get("minimum_instances", 800):
            report["blockers"].append("Insufficient spalling instances.")
        if report["efflorescence_instances"] < dt_dist.get("efflorescence", {}).get("minimum_instances", 800):
            report["blockers"].append("Insufficient efflorescence instances.")
            
        hn_dist = self.targets.get("hard_negative_target", {})
        if report["hard_negatives"] < hn_dist.get("minimum_instances", 800):
            report["blockers"].append("Insufficient hard negatives.")
            
        if not report["blockers"]:
            report["status"] = "PASS"
        else:
            # Explicitly mark as BLOCKED when actual data is insufficient for ML readiness
            report["status"] = "BLOCKED"
            
        return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", required=True, type=Path)
    parser.add_argument("--metadata", required=True, type=Path)
    args = parser.parse_args()
    checker = FieldDataReadinessChecker(args.targets)
    res = checker.check_readiness(args.metadata)
    print(json.dumps(res, indent=4, default=list))
