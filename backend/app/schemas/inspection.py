from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class InspectionBase(BaseModel):
    notes: Optional[str] = None
    building_id: str
    # The structural element being inspected. Optional so existing routes
    # remain backwards-compatible, but should always be provided by the UI.
    structural_element_id: Optional[str] = None

class InspectionCreate(InspectionBase):
    pass

class InspectionResponse(InspectionBase):
    id: str
    inspector_id: str
    assigned_engineer_id: Optional[str] = None
    status: str
    structural_element_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)

