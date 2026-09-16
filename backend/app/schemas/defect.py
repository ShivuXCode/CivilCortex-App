from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class DefectBase(BaseModel):
    defect_type: str
    status: Optional[str] = "CANDIDATE"

class DefectCreate(DefectBase):
    structural_element_id: str

class DefectResponse(DefectBase):
    id: str
    structural_element_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DefectUpdate(BaseModel):
    status: str

class AssessmentBase(BaseModel):
    severity: str
    risk: str
    repair_recommendation: Optional[str] = None

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentUpdate(BaseModel):
    severity: Optional[str] = None
    risk: Optional[str] = None
    repair_recommendation: Optional[str] = None

class AssessmentResponse(AssessmentBase):
    id: str
    observation_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CrackObservationBase(BaseModel):
    pass

class CrackObservationCreate(CrackObservationBase):
    defect_id: str
    inspection_id: str
    image_id: str

class CrackObservationResponse(CrackObservationBase):
    id: str
    defect_id: str
    inspection_id: str
    image_id: str
    created_at: datetime
    assessment: Optional[AssessmentResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ReportResponse(BaseModel):
    content: str
    generated_at: datetime
    status: str
