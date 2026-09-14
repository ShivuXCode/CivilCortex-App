from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DefectBase(BaseModel):
    defect_type: str
    status: Optional[str] = "CANDIDATE"

class DefectCreate(DefectBase):
    structural_element_id: str

class DefectResponse(DefectBase):
    id: str
    structural_element_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DefectUpdate(BaseModel):
    status: str

class AssessmentBase(BaseModel):
    severity: str
    risk: str
    repair_recommendation: Optional[str] = None

class AssessmentCreate(AssessmentBase):
    pass

class AssessmentResponse(AssessmentBase):
    id: str
    observation_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

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

    class Config:
        from_attributes = True
