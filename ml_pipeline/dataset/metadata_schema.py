from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json
from datetime import datetime

@dataclass
class AnnotationMetadata:
    annotator_id: str
    timestamp: datetime
    tool_version: str

@dataclass
class DefectInstance:
    defect_instance_id: str
    defect_type: str
    morphology_labels: List[str] = field(default_factory=list)
    
    # Annotation representation
    annotation_type: str = "POLYGON" # MASK, POLYGON, BBOX, CLASSIFICATION
    original_dataset_label: str = ""
    mapping_status: str = "DIRECT" # DIRECT, PARTIAL, AMBIGUOUS, UNMAPPED, NOT_APPLICABLE
    mapping_confidence: str = "HIGH"
    
    polygon: Optional[List[List[float]]] = None # List of [x, y] points
    bounding_box: Optional[List[float]] = None # [x_min, y_min, x_max, y_max]
    mask_path: Optional[str] = None
    original_annotation_path: Optional[str] = None

    def model_dump(self):
        return asdict(self)

@dataclass
class CalibrationData:
    is_calibrated: bool = False
    reference_object: Optional[str] = None
    pixels_per_mm: Optional[float] = None

@dataclass
class ImageMetadata:
    # Required Fields
    source_id: str
    image_id: str
    image_width: int
    image_height: int

    # Optional / Default Fields
    site_id: Optional[str] = None
    building_id: Optional[str] = None
    floor_id: Optional[str] = None
    area_id: Optional[str] = None
    structural_element_id: Optional[str] = None
    inspection_id: Optional[str] = None
    observation_id: Optional[str] = None
    
    # Provenance
    acquisition_date: Optional[str] = None
    capture_device: Optional[str] = None
    original_resolution: Optional[str] = None
    preprocessing_history: List[str] = field(default_factory=list)
    annotation_version: Optional[str] = None
    dataset_version: Optional[str] = None
    license: Optional[str] = None
    
    # Ingestion Status & Audit
    license_status: str = "UNVERIFIED"
    provenance_status: str = "VALID" # VALID, PARTIAL, INVALID, UNVERIFIED, RESEARCH_ONLY, REJECTED
    duplicate_group_id: Optional[str] = None
    production_training_eligible: bool = False
    
    # Image properties
    quality_status: str = "PENDING" # PENDING, PASS, REJECTED
    calibration: CalibrationData = field(default_factory=CalibrationData)
    defects: List[DefectInstance] = field(default_factory=list)
    annotation_info: Optional[AnnotationMetadata] = None

    def model_dump_json(self, indent=None):
        return json.dumps(asdict(self), indent=indent, default=str)
