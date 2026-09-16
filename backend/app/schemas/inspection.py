from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InspectionBase(BaseModel):
    notes: Optional[str] = None
    building_id: str

class InspectionCreate(InspectionBase):
    pass

class InspectionResponse(InspectionBase):
    id: str
    inspector_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InspectionImageBase(BaseModel):
    inspection_id: str
    original_filename: str
    mime_type: str
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

class InspectionImageResponse(InspectionImageBase):
    id: str
    object_key: str
    created_at: datetime

    class Config:
        from_attributes = True
