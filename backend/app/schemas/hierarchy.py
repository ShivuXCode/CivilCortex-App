from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class BuildingBase(BaseModel):
    name: str
    location: Optional[str] = None

class BuildingCreate(BuildingBase):
    pass

class BuildingResponse(BuildingBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FloorBase(BaseModel):
    name: str
    level: Optional[int] = 0

class FloorCreate(FloorBase):
    building_id: str

class FloorResponse(FloorBase):
    id: str
    building_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AreaBase(BaseModel):
    name: str

class AreaCreate(AreaBase):
    floor_id: str

class AreaResponse(AreaBase):
    id: str
    floor_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StructuralElementBase(BaseModel):
    name: str
    element_type: str

class StructuralElementCreate(StructuralElementBase):
    area_id: str

class StructuralElementResponse(StructuralElementBase):
    id: str
    area_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

