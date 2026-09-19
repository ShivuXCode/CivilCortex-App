from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import User, Inspection, Building, InspectionImage
from app.models.analysis import AnalysisJob
from app.schemas.inspection import (
    InspectionCreate, InspectionResponse,
    InspectionImageResponse
)
import app.schemas.defect
from app.models.defect import CrackObservation, Assessment
from app.services.image_service import ImageService
from app.services.ml_service import MLService
from app.worker import analysis_queue, run_analysis_job
from app.core.limiter import limiter

router = APIRouter()

@router.post("/", response_model=InspectionResponse)
def create_inspection(inspection: InspectionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    building = db.query(Building).filter(Building.id == inspection.building_id, Building.organization_id == current_user.organization_id).first()
    if not building:
        raise HTTPException(status_code=403, detail="Building not found or access denied")

    db_obj = Inspection(**inspection.model_dump(), inspector_id=current_user.id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[InspectionResponse])
def get_inspections(skip: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Inspection).join(Building).filter(Building.organization_id == current_user.organization_id).offset(skip).limit(limit).all()

@router.post("/{inspection_id}/images", response_model=InspectionImageResponse)
def upload_inspection_image(
    inspection_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    inspection = db.query(Inspection).join(Building).filter(Inspection.id == inspection_id, Building.organization_id == current_user.organization_id).first()
    if not inspection:
        raise HTTPException(status_code=403, detail="Inspection not found or access denied")
    
    image_info = ImageService.save_image(file, inspection_id)
    db_image = InspectionImage(
        inspection_id=inspection_id,
        object_key=image_info["object_key"],
        original_filename=image_info["original_filename"],
        mime_type=image_info["mime_type"],
        file_size=image_info["file_size"]
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@router.post("/{inspection_id}/images/{image_id}/analyze")
@limiter.limit("20/minute")
def analyze_image(
    request: Request,
    inspection_id: str,
    image_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.worker import analysis_queue, run_analysis_job

    # 1. Check if image belongs to inspection and inspection belongs to user
    image = db.query(InspectionImage).filter(
        InspectionImage.id == image_id,
        InspectionImage.inspection_id == inspection_id
    ).first()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found in this inspection")
        
    inspection = db.query(Inspection).join(Building).filter(
        Inspection.id == inspection_id,
        Building.organization_id == current_user.organization_id
    ).first()
    
    if not inspection:
        raise HTTPException(status_code=403, detail="Inspection not found or access denied")
        
    # 2. Check if a job already exists for this image (Idempotency)
    existing_job = db.query(AnalysisJob).filter(AnalysisJob.image_id == image_id).first()
    if existing_job:
        # If it's already queued/processing/completed, just return it
        if existing_job.status in ["QUEUED", "PROCESSING", "COMPLETED"]:
            return {"job_id": existing_job.id, "status": existing_job.status, "message": "Job already exists"}
        # If it failed previously, we will let it create a new job or overwrite. 
        # Actually, let's just use the existing job and reset it
        existing_job.status = "QUEUED"
        existing_job.error_message = None
        db.commit()
        job = existing_job
    else:
        # Create new job
        job = AnalysisJob(image_id=image_id, status="QUEUED")
        db.add(job)
        db.commit()
        db.refresh(job)
    
    # 3. Enqueue the task to RQ
    analysis_queue.enqueue(run_analysis_job, job_id=str(job.id))
    
    return {"job_id": job.id, "status": job.status, "message": "Analysis job queued successfully"}

@router.get("/{inspection_id}/assessment", response_model=List[app.schemas.defect.AssessmentResponse])
def get_inspection_assessments(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    inspection = db.query(Inspection).join(Building).filter(
        Inspection.id == inspection_id,
        Building.organization_id == current_user.organization_id
    ).first()
    
    if not inspection:
        raise HTTPException(status_code=403, detail="Inspection not found or access denied")
        
    assessments = db.query(Assessment).join(CrackObservation).filter(
        CrackObservation.inspection_id == inspection_id
    ).all()
    
    return assessments

@router.get("/{inspection_id}/report", response_model=app.schemas.defect.ReportResponse)
def get_inspection_report(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    inspection = db.query(Inspection).join(Building).filter(
        Inspection.id == inspection_id,
        Building.organization_id == current_user.organization_id
    ).first()
    
    if not inspection:
        raise HTTPException(status_code=403, detail="Inspection not found or access denied")
        
    assessment = db.query(Assessment).join(CrackObservation).filter(
        CrackObservation.inspection_id == inspection_id,
        Assessment.llm_report.isnot(None)
    ).order_by(Assessment.created_at.desc()).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="No report generated for this inspection yet")
        
    return {
        "content": assessment.llm_report,
        "generated_at": assessment.updated_at,
        "status": "COMPLETED"
    }
