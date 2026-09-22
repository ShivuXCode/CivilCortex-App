from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_user, get_inspector_user, get_engineer_user, get_admin_user
from app.models import User, Inspection, Building, InspectionImage
from app.models.analysis import AnalysisJob
from app.schemas.inspection import (
    InspectionCreate, InspectionResponse,
    InspectionImageResponse
)
from sqlalchemy import or_
import app.schemas.defect
from app.models.defect import CrackObservation, Assessment
from app.services.image_service import ImageService
from app.services.ml_service import MLService
from app.worker import analysis_queue, run_analysis_job
from app.core.limiter import limiter

router = APIRouter()

@router.post("/", response_model=InspectionResponse)
def create_inspection(inspection: InspectionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_inspector_user)):
    building = db.query(Building).filter(Building.id == inspection.building_id, Building.organization_id == current_user.organization_id).first()
    if not building:
        raise HTTPException(status_code=403, detail="Building not found or access denied")

    db_obj = Inspection(**inspection.model_dump(), inspector_id=current_user.id, status="DRAFT")
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

from app.api.deps import ENFORCE_RBAC

@router.get("/", response_model=List[InspectionResponse])
def get_inspections(skip: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=100), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Inspection).join(Building).filter(Building.organization_id == current_user.organization_id)
    
    if ENFORCE_RBAC:
        if current_user.role == "INSPECTOR":
            query = query.filter(Inspection.inspector_id == current_user.id)
        elif current_user.role == "ENGINEER":
            # Engineers see what is assigned to them, or anything that is pending assignment (for a queue view)
            query = query.filter(or_(
                Inspection.assigned_engineer_id == current_user.id,
                Inspection.status.in_(["SUBMITTED", "AI_ANALYSIS", "ASSESSMENT_READY"])
            ))
    
    return query.offset(skip).limit(limit).all()

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
    if analysis_queue:
        analysis_queue.enqueue(run_analysis_job, job_id=str(job.id))
    else:
        # Run synchronously in background if Redis is disabled
        import threading
        threading.Thread(target=run_analysis_job, args=(str(job.id),)).start()
    
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
        
    if inspection.status not in ["REPORT_GENERATED", "COMPLETED", "APPROVED"]:
        raise HTTPException(status_code=400, detail="Report is not available for this inspection state")
        
    assessment = db.query(Assessment).join(CrackObservation).filter(
        CrackObservation.inspection_id == inspection_id
    ).order_by(Assessment.created_at.desc()).first()
    
    if not assessment or (not assessment.repair_recommendation and not assessment.llm_report):
        raise HTTPException(status_code=404, detail="No report content generated for this inspection yet")
        
    return {
        "content": assessment.repair_recommendation or assessment.llm_report,
        "generated_at": assessment.updated_at,
        "status": inspection.status
    }

from pydantic import BaseModel

@router.post("/{inspection_id}/submit")
def submit_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_inspector_user)
):
    inspection = db.query(Inspection).join(Building).filter(
        Inspection.id == inspection_id,
        Building.organization_id == current_user.organization_id,
        Inspection.inspector_id == current_user.id
    ).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if inspection.status not in ["DRAFT", "REVISION_REQUIRED", "ASSESSMENT_READY", "AI_ANALYSIS"]:
        raise HTTPException(status_code=400, detail="Inspection cannot be submitted in its current state")
    
    inspection.status = "SUBMITTED"
    db.commit()
    return {"status": inspection.status}



@router.post("/{inspection_id}/begin-review")
def begin_review(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_engineer_user)
):
    inspection = db.query(Inspection).join(Building).filter(
        Inspection.id == inspection_id,
        Building.organization_id == current_user.organization_id
    ).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if inspection.status not in ["SUBMITTED", "ASSESSMENT_READY"]:
        raise HTTPException(status_code=400, detail="Inspection is not ready for review")
        
    inspection.status = "UNDER_ENGINEER_REVIEW"
    db.commit()
    return {"status": inspection.status}


class RevisionRequest(BaseModel):
    reason: str

@router.post("/{inspection_id}/request-revision")
def request_revision(
    inspection_id: str,
    data: RevisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_engineer_user)
):
    inspection = db.query(Inspection).join(Building).filter(
        Inspection.id == inspection_id,
        Building.organization_id == current_user.organization_id
    ).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if inspection.status != "UNDER_ENGINEER_REVIEW":
        raise HTTPException(status_code=400, detail="Inspection must be UNDER_ENGINEER_REVIEW to request a revision")
        
    inspection.status = "REVISION_REQUIRED"
    inspection.notes = (inspection.notes or "") + f"\n\nRevision requested: {data.reason}"
    db.commit()
    return {"status": inspection.status}


@router.post("/{inspection_id}/approve")
def approve_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_engineer_user)
):
    inspection = db.query(Inspection).join(Building).filter(
        Inspection.id == inspection_id,
        Building.organization_id == current_user.organization_id
    ).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    if inspection.status != "UNDER_ENGINEER_REVIEW":
        raise HTTPException(status_code=400, detail="Inspection must be UNDER_ENGINEER_REVIEW to approve")
        
    inspection.status = "APPROVED"
    db.commit()
    return {"status": inspection.status}

@router.post("/{inspection_id}/generate-report")
def generate_report_retry(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_engineer_user)
):
    inspection = db.query(Inspection).join(Building).filter(
        Inspection.id == inspection_id,
        Building.organization_id == current_user.organization_id
    ).first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    if inspection.status not in ["APPROVED", "REPORT_GENERATED"]:
        raise HTTPException(status_code=400, detail="Inspection must be APPROVED to generate report")
        
    assessment = db.query(Assessment).join(CrackObservation).filter(
        CrackObservation.inspection_id == inspection_id
    ).order_by(Assessment.created_at.desc()).first()
    
    if not assessment:
        raise HTTPException(status_code=400, detail="No assessment found to generate report from")
        
    from langchain_google_genai import ChatGoogleGenerativeAI
    prompt = f"""
    Act as a Lead Civil Engineer.
    Write a final Executive Engineering Report for a structural inspection.
    
    Inspection Data:
    - Defect Severity: {assessment.severity}
    - Overall Risk Level: {assessment.risk}
    - Priority: {assessment.priority}
    - Engineer's Action Plan: {assessment.repair_recommendation}
    
    RAG Context:
    {assessment.rag_context or "No specific standards retrieved."}
    
    Please provide a professional, executive-level summary of the findings, the risk, and the recommended repair actions in Markdown format. Ensure you cite the standards if they apply.
    """
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
        response = llm.invoke(prompt)
        report_content = response.content
    except Exception as e:
        import logging
        logging.error(f"Failed to generate LLM report: {e}")
        report_content = f"### Executive Report\n\n**Severity:** {assessment.severity}\n**Risk:** {assessment.risk}\n\n**Engineer's Action Plan:**\n{assessment.repair_recommendation}\n\n*(Note: LLM generation failed. Showing raw assessment data.)*"
        
    assessment.llm_report = report_content
    assessment.updated_at = __import__('datetime').datetime.utcnow()
    inspection.status = "COMPLETED"
    db.commit()
    
    return {"status": inspection.status, "message": "Report generated successfully"}
