from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import User, Inspection, Building, InspectionImage
from app.schemas.inspection import (
    InspectionCreate, InspectionResponse,
    InspectionImageResponse
)
from app.services.image_service import ImageService
from app.services.ml_service import MLService

router = APIRouter()

@router.post("/", response_model=InspectionResponse)
def create_inspection(inspection: InspectionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    building = db.query(Building).filter(Building.id == inspection.building_id, Building.owner_id == current_user.id).first()
    if not building:
        raise HTTPException(status_code=403, detail="Building not found or access denied")
    
    db_obj = Inspection(**inspection.model_dump(), inspector_id=current_user.id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[InspectionResponse])
def get_inspections(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Inspection).filter(Inspection.inspector_id == current_user.id).all()

@router.post("/{inspection_id}/images", response_model=InspectionImageResponse)
def upload_inspection_image(
    inspection_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inspection = db.query(Inspection).filter(Inspection.id == inspection_id, Inspection.inspector_id == current_user.id).first()
    if not inspection:
        raise HTTPException(status_code=403, detail="Inspection not found or access denied")
    
    image_info = ImageService.save_image(file)
    db_image = InspectionImage(
        inspection_id=inspection_id,
        file_path=image_info["file_path"],
        original_filename=image_info["original_filename"],
        mime_type=image_info["mime_type"],
        file_size=image_info["file_size"]
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@router.post("/{inspection_id}/images/{image_id}/analyze")
def analyze_image(
    inspection_id: str,
    image_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify ownership
    image = db.query(InspectionImage).join(Inspection).filter(
        InspectionImage.id == image_id,
        Inspection.id == inspection_id,
        Inspection.inspector_id == current_user.id
    ).first()
    
    if not image:
        raise HTTPException(status_code=403, detail="Image not found or access denied")
        
    analysis_result = MLService.analyze_image(image.file_path)
    return analysis_result
