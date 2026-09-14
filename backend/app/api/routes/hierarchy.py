from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import User, Building, Floor, Area, StructuralElement
from app.schemas.hierarchy import (
    BuildingCreate, BuildingResponse,
    FloorCreate, FloorResponse,
    AreaCreate, AreaResponse,
    StructuralElementCreate, StructuralElementResponse
)
from pydantic import BaseModel

class StructuralElementDetail(StructuralElementResponse):
    pass

class AreaDetail(AreaResponse):
    structural_elements: List[StructuralElementDetail] = []

class FloorDetail(FloorResponse):
    areas: List[AreaDetail] = []

class BuildingDetail(BuildingResponse):
    floors: List[FloorDetail] = []

router = APIRouter()

# --- Buildings ---
@router.post("/buildings", response_model=BuildingResponse)
def create_building(building: BuildingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_obj = Building(**building.model_dump(), owner_id=current_user.id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/buildings", response_model=List[BuildingResponse])
def get_buildings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Building).filter(Building.owner_id == current_user.id).all()

@router.get("/buildings/{building_id}", response_model=BuildingDetail)
def get_building(building_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    building = db.query(Building).filter(Building.id == building_id, Building.owner_id == current_user.id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building

# --- Floors ---
@router.post("/floors", response_model=FloorResponse)
def create_floor(floor: FloorCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    building = db.query(Building).filter(Building.id == floor.building_id, Building.owner_id == current_user.id).first()
    if not building:
        raise HTTPException(status_code=403, detail="Building not found or access denied")
    db_obj = Floor(**floor.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- Areas ---
@router.post("/areas", response_model=AreaResponse)
def create_area(area: AreaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    floor = db.query(Floor).filter(Floor.id == area.floor_id).first()
    if not floor or floor.building.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Floor not found or access denied")
    db_obj = Area(**area.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- Structural Elements ---
@router.post("/structural-elements", response_model=StructuralElementResponse)
def create_structural_element(element: StructuralElementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    area = db.query(Area).filter(Area.id == element.area_id).first()
    if not area or area.floor.building.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Area not found or access denied")
    db_obj = StructuralElement(**element.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
