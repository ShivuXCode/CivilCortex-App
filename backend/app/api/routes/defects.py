from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import User, Defect, StructuralElement, CrackObservation, InspectionImage, Assessment, Building, Floor, Area
from app.schemas.defect import (
    DefectCreate, DefectResponse, DefectUpdate,
    CrackObservationCreate, CrackObservationResponse,
    AssessmentCreate, AssessmentResponse
)

router = APIRouter()

VALID_TRANSITIONS = {
    "CANDIDATE": ["MONITORED", "DISMISSED"],
    "MONITORED": ["REPAIRED"],
    "REPAIRED": ["MONITORED"],
    "DISMISSED": []
}

@router.get("/", response_model=List[DefectResponse])
def get_defects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Defect).join(StructuralElement).join(Area).join(Floor).join(Building).filter(
        Building.owner_id == current_user.id
    ).all()

@router.post("/", response_model=DefectResponse)
def create_defect(defect: DefectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    element = db.query(StructuralElement).filter(StructuralElement.id == defect.structural_element_id).first()
    if not element or element.area.floor.building.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Structural Element not found or access denied")
    
    db_obj = Defect(**defect.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/{defect_id}", response_model=DefectResponse)
def update_defect_status(defect_id: str, defect_update: DefectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect or defect.structural_element.area.floor.building.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Defect not found or access denied")
    
    new_status = defect_update.status
    if new_status not in VALID_TRANSITIONS.get(defect.status, []):
        raise HTTPException(status_code=400, detail=f"Invalid state transition from {defect.status} to {new_status}")
    
    defect.status = new_status
    db.commit()
    db.refresh(defect)
    return defect

@router.post("/observations", response_model=CrackObservationResponse)
def create_observation(obs: CrackObservationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Verify defect access
    defect = db.query(Defect).filter(Defect.id == obs.defect_id).first()
    if not defect or defect.structural_element.area.floor.building.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Defect not found or access denied")
    
    # Create observation
    db_obj = CrackObservation(**obs.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.post("/observations/{observation_id}/assessments", response_model=AssessmentResponse)
def create_assessment(observation_id: str, assessment: AssessmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obs = db.query(CrackObservation).filter(CrackObservation.id == observation_id).first()
    if not obs or obs.defect.structural_element.area.floor.building.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Observation not found or access denied")
    
    existing = db.query(Assessment).filter(Assessment.observation_id == observation_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Assessment already exists for this observation")
        
    db_obj = Assessment(**assessment.model_dump(), observation_id=observation_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
