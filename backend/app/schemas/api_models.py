from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# Common
class HealthScore(BaseModel):
    score: int
    level: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Users
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Buildings
class BuildingBase(BaseModel):
    name: str
    type: Optional[str] = "Commercial"

class BuildingCreate(BuildingBase):
    pass

class BuildingResponse(BuildingBase):
    id: int
    health_score: Optional[int] = 100
    user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Inspections
class InspectionBase(BaseModel):
    title: Optional[str] = None
    building_id: Optional[int] = None
    status: str = "completed"

class InspectionCreate(InspectionBase):
    pass

class InspectionResponse(InspectionBase):
    id: int
    inspector_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Cracks
class CrackBase(BaseModel):
    element_id: Optional[int] = None
    status: str = "active"

class CrackCreate(CrackBase):
    pass

class CrackResponse(CrackBase):
    id: int
    first_detected_at: datetime
    model_config = ConfigDict(from_attributes=True)


from pydantic import BaseModel, ConfigDict, Field, model_validator, validator, ConfigDict

class CVMeasurement(BaseModel):
    pixel_length: Optional[float] = None
    pixel_width: Optional[float] = None
    physical_length: Optional[float] = None
    physical_width: Optional[float] = None
    measurement_unit: str = "px"
    measurement_method: str = "medial_axis_extraction"
    calibration_status: str = "UNAVAILABLE" # UNAVAILABLE, PIXEL_ONLY, PHYSICAL_CALIBRATED, PHYSICAL_ESTIMATED
    calibration_reference: Optional[str] = None
    uncertainty: Optional[float] = None

    @model_validator(mode='after')
    def validate_calibration_rules(self):
        if self.calibration_status in ["PIXEL_ONLY", "UNAVAILABLE"]:
            if self.physical_length is not None or self.physical_width is not None:
                raise ValueError(f"Cannot contain physical dimensions when status is {self.calibration_status}")
        
        if self.calibration_status == "PHYSICAL_CALIBRATED":
            if not self.calibration_reference:
                raise ValueError("PHYSICAL_CALIBRATED requires a calibration_reference")
        
        return self

class CVGeometry(BaseModel):
    orientation_degrees: Optional[float] = None

class CVDetection(BaseModel):
    detection_id: str
    defect_type: str
    morphology_tags: List[str] = []
    model_confidence: float
    bounding_box: List[float] # [x_min, y_min, x_max, y_max]
    segmentation_mask_ref: Optional[str] = None
    geometry: Optional[CVGeometry] = None
    measurement: Optional[CVMeasurement] = None

class ImageQualityResult(BaseModel):
    quality_score: float
    is_pass: bool
    rejection_reasons: List[str] = []

class CVAnalysisResult(BaseModel):
    image_id: Optional[str] = None
    model_version: str = "PIPELINE_DEMO_ONLY"
    inference_timestamp: datetime
    image_width: int
    image_height: int
    coordinate_convention: str = "top_left_origin"
    quality: ImageQualityResult
    image_status: str = "NO_DEFECT"
    detections: List[CVDetection] = []

# Candidate Matches
class CandidateMatch(BaseModel):
    crack_id: int
    confidence_score: float
    reasons: List[str]

# Observations
class ObservationBase(BaseModel):
    crack_id: int
    inspection_id: int
    image_id: Optional[int] = None
    classification_type: Optional[str] = None
    pixel_length: Optional[float] = None
    length_mm: Optional[float] = None
    width_mm: Optional[float] = None
    measurement_status: str = "UNAVAILABLE" # PIXEL, CALIBRATED, ESTIMATED, UNAVAILABLE
    orientation_degrees: Optional[float] = None
    notes: Optional[str] = None

class ObservationResponse(ObservationBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Assessments
class SeverityAssessmentResponse(BaseModel):
    id: int
    observation_id: int
    level: str
    score: Optional[float]
    factors_json: Optional[Dict[str, Any]]
    model_config = ConfigDict(from_attributes=True)


class RiskAssessmentResponse(BaseModel):
    id: int
    observation_id: int
    level: str
    score: float
    factors_json: Optional[Dict[str, Any]]
    model_config = ConfigDict(from_attributes=True)


class PriorityAssessmentResponse(BaseModel):
    id: int
    observation_id: int
    level: str
    max_days: Optional[int]
    factors_json: Optional[Dict[str, Any]]
    model_config = ConfigDict(from_attributes=True)


class CostEstimateResponse(BaseModel):
    id: int
    currency: str
    material_cost: float
    labor_cost: float
    total_range_low: float
    total_range_high: float
    details_json: Optional[Dict[str, Any]]
    model_config = ConfigDict(from_attributes=True)


class RepairPlanResponse(BaseModel):
    id: int
    method_name: str
    description: Optional[str]
    cost_estimate: Optional[CostEstimateResponse]
    model_config = ConfigDict(from_attributes=True)


class ObservationCreate(BaseModel):
    image_base64: Optional[str] = None
    cv_detection: Optional[CVDetection] = None
    severity_level: str
    element_type: str

class CandidateConfirmationRequest(BaseModel):
    decision: str = Field(..., description="'EXISTING' or 'NEW'")
    crack_id: Optional[int] = Field(None, description="Required if decision is 'EXISTING'")
    observation_data: ObservationCreate


