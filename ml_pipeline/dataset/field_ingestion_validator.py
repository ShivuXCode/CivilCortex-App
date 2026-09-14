import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import collections

class FieldIngestionValidator:
    def __init__(self):
        # Tracking hierarchy mappings for cross-record consistency
        self.image_to_observation = {}
        self.observation_to_inspection = {}
        self.defect_to_element = {}
        self.element_to_area = {}
        self.area_to_floor = {}
        self.floor_to_building = {}
        self.building_to_site = {}
        self.image_hashes = set()
        
    def _validate_hierarchy(self, record: Dict[str, Any]) -> List[str]:
        errors = []
        req_fields = [
            "source_id", "site_id", "building_id", "floor_id", "area_id",
            "structural_element_id", "inspection_id", "observation_id", "image_id"
        ]
        
        for f in req_fields:
            if not record.get(f):
                errors.append(f"Missing required hierarchy field: {f}")
                
        if errors:
            return errors # Stop hierarchy validation if missing fields

        # Cross-record validation
        img = record['image_id']
        obs = record['observation_id']
        ins = record['inspection_id']
        bld = record['building_id']
        flr = record['floor_id']
        are = record['area_id']
        ele = record['structural_element_id']
        sit = record['site_id']

        if img in self.image_to_observation and self.image_to_observation[img] != obs:
            errors.append(f"Hierarchy mismatch: image {img} assigned to multiple observations.")
        else:
            self.image_to_observation[img] = obs

        if obs in self.observation_to_inspection and self.observation_to_inspection[obs] != ins:
            errors.append(f"Hierarchy mismatch: observation {obs} assigned to multiple inspections.")
        else:
            self.observation_to_inspection[obs] = ins
            
        if bld in self.building_to_site and self.building_to_site[bld] != sit:
            errors.append(f"Hierarchy mismatch: building {bld} assigned to multiple sites.")
        else:
            self.building_to_site[bld] = sit
            
        if flr in self.floor_to_building and self.floor_to_building[flr] != bld:
            errors.append(f"Hierarchy mismatch: floor {flr} assigned to multiple buildings.")
        else:
            self.floor_to_building[flr] = bld
            
        if are in self.area_to_floor and self.area_to_floor[are] != flr:
            errors.append(f"Hierarchy mismatch: area {are} assigned to multiple floors.")
        else:
            self.area_to_floor[are] = flr
            
        if ele in self.element_to_area and self.element_to_area[ele] != are:
            errors.append(f"Hierarchy mismatch: element {ele} assigned to multiple areas.")
        else:
            self.element_to_area[ele] = are

        # Track defects
        for d in record.get('defect_instances', []):
            did = d.get('defect_instance_id')
            if not did:
                errors.append(f"Missing defect_instance_id in record {img}")
                continue
            if did in self.defect_to_element and self.defect_to_element[did] != ele:
                errors.append(f"Hierarchy mismatch: defect {did} assigned to multiple structural elements.")
            else:
                self.defect_to_element[did] = ele

        return errors

    def _validate_schema(self, record: Dict[str, Any]) -> List[str]:
        errors = []
        if not record.get("schema_version"): errors.append("Missing schema_version")
        if not record.get("dataset_version"): errors.append("Missing dataset_version")
        if not record.get("annotation_version"): errors.append("Missing annotation_version")
        return errors

    def _validate_privacy(self, record: Dict[str, Any]) -> List[str]:
        status = record.get("privacy_status")
        if not status:
            return ["Missing privacy_status"]
        if status not in ["ACCEPT", "REDACT", "REJECT", "PENDING"]:
            return [f"Invalid privacy_status: {status}"]
        return []

    def _validate_taxonomy(self, record: Dict[str, Any]) -> List[str]:
        errors = []
        valid_types = ["crack", "spalling", "efflorescence", "hard_negative"]
        valid_morph = ["horizontal", "vertical", "diagonal", "branching", "irregular", "UNKNOWN", "UNCERTAIN"]
        
        for d in record.get('defect_instances', []):
            dtype = d.get('defect_type')
            if dtype not in valid_types:
                errors.append(f"Invalid defect type: {dtype}")
                
            for m in d.get('morphology_labels', []):
                if m not in valid_morph:
                    errors.append(f"Invalid morphology tag: {m}")
                    
        return errors

    def _validate_calibration(self, record: Dict[str, Any]) -> List[str]:
        errors = []
        cal_status = record.get("calibration_status")
        if cal_status not in ["PIXEL_ONLY", "PHYSICAL_CALIBRATED", "ESTIMATED", "UNAVAILABLE"]:
            errors.append(f"Invalid calibration status: {cal_status}")
            
        phys_measure = record.get("physical_measurements", {})
        if phys_measure and cal_status not in ["PHYSICAL_CALIBRATED", "ESTIMATED"]:
            errors.append(f"Physical measurements present but calibration status is {cal_status}")
            
        return errors
        
    def _validate_duplicates(self, record: Dict[str, Any]) -> List[str]:
        errors = []
        h = record.get("checksum")
        if not h:
            return ["Missing checksum"]
        if h in self.image_hashes:
            errors.append(f"Duplicate image checksum found: {h}")
        else:
            self.image_hashes.add(h)
        return errors

    def validate_record(self, record: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Returns (status, errors)
        status: VALID, INVALID, WARNING, REVIEW_REQUIRED
        """
        errors = []
        
        errors.extend(self._validate_schema(record))
        errors.extend(self._validate_hierarchy(record))
        errors.extend(self._validate_privacy(record))
        errors.extend(self._validate_taxonomy(record))
        errors.extend(self._validate_calibration(record))
        errors.extend(self._validate_duplicates(record))
        
        if len(errors) > 0:
            return "INVALID", errors
            
        if record.get("privacy_status") == "REVIEW_REQUIRED":
            return "REVIEW_REQUIRED", []
            
        return "VALID", []

