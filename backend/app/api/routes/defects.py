from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import User, Defect, StructuralElement, CrackObservation, InspectionImage, Assessment, Building, Floor, Area, Inspection
from app.schemas.defect import (
    DefectCreate, DefectResponse, DefectUpdate,
    CrackObservationCreate, CrackObservationResponse,
    AssessmentCreate, AssessmentResponse
)
import app.schemas.defect

router = APIRouter()

VALID_TRANSITIONS = {
    "CANDIDATE": ["MONITORED", "DISMISSED"],
    "MONITORED": ["REPAIRED"],
    "REPAIRED": ["MONITORED"],
    "DISMISSED": []
}

from fastapi import Query

@router.get("/", response_model=List[DefectResponse])
def get_defects(skip: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Use outerjoin (LEFT JOIN) instead of join (INNER JOIN).
    # AI-generated defects have structural_element_id=NULL and were silently
    # excluded by the previous INNER JOIN chain, making them invisible in the UI.
    return (
        db.query(Defect)
        .outerjoin(StructuralElement, Defect.structural_element_id == StructuralElement.id)
        .outerjoin(Area, StructuralElement.area_id == Area.id)
        .outerjoin(Floor, Area.floor_id == Floor.id)
        .outerjoin(Building, Floor.building_id == Building.id)
        .filter(
            # Include defects either belonging to this org's elements OR with no element
            (Building.organization_id == current_user.organization_id) | (Defect.structural_element_id.is_(None))
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

@router.post("/", response_model=DefectResponse)
def create_defect(defect: DefectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    element = db.query(StructuralElement).options(joinedload(StructuralElement.area).joinedload(Area.floor).joinedload(Floor.building)).filter(StructuralElement.id == defect.structural_element_id).first()
    if not element or element.area.floor.building.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Structural Element not found or access denied")
    
    db_obj = Defect(**defect.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.put("/{defect_id}", response_model=DefectResponse)
def update_defect_status(defect_id: str, defect_update: DefectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    defect = db.query(Defect).options(joinedload(Defect.structural_element).joinedload(StructuralElement.area).joinedload(Area.floor).joinedload(Floor.building)).filter(Defect.id == defect_id).first()
    if not defect or defect.structural_element.area.floor.building.organization_id != current_user.organization_id:
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
    defect = db.query(Defect).options(joinedload(Defect.structural_element).joinedload(StructuralElement.area).joinedload(Area.floor).joinedload(Floor.building)).filter(Defect.id == obs.defect_id).first()
    if not defect or defect.structural_element.area.floor.building.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Defect not found or access denied")
    
    # Create observation
    db_obj = CrackObservation(**obs.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.post("/observations/{observation_id}/assessments", response_model=AssessmentResponse)
def create_assessment(observation_id: str, assessment: AssessmentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    obs = db.query(CrackObservation).options(joinedload(CrackObservation.defect).joinedload(Defect.structural_element).joinedload(StructuralElement.area).joinedload(Area.floor).joinedload(Floor.building)).filter(CrackObservation.id == observation_id).first()
    if not obs or obs.defect.structural_element.area.floor.building.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Observation not found or access denied")
    
    existing = db.query(Assessment).filter(Assessment.observation_id == observation_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Assessment already exists for this observation")
        
    db_obj = Assessment(**assessment.model_dump(), observation_id=observation_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

from app.api.deps import RoleChecker

@router.patch("/assessments/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(
    assessment_id: str,
    assessment_update: app.schemas.defect.AssessmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["ENGINEER", "ADMIN"]))
):
    assessment = db.query(Assessment).options(
        joinedload(Assessment.observation).joinedload(CrackObservation.defect).joinedload(Defect.structural_element).joinedload(StructuralElement.area).joinedload(Area.floor).joinedload(Floor.building),
        joinedload(Assessment.observation).joinedload(CrackObservation.inspection).joinedload(Inspection.building)
    ).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    # Verify ownership through the observation -> defect -> structural_element -> area -> floor -> building
    if assessment.observation.defect.structural_element:
        org_id = assessment.observation.defect.structural_element.area.floor.building.organization_id
    else:
        # If defect has no structural element, check the inspection's building
        org_id = assessment.observation.inspection.building.organization_id
        
    if org_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
        
    update_data = assessment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(assessment, key, value)
        
    db.commit()
    db.refresh(assessment)
    return assessment
