from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models import User, AnalysisJob, InspectionImage, Inspection, Building
from app.schemas.analysis import AnalysisJobResponse

router = APIRouter()

@router.get("/{job_id}", response_model=AnalysisJobResponse)
def get_analysis_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Retrieve the job
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")
        
    # Verify ownership: Job -> Image -> Inspection -> owner (inspector_id)
    image = db.query(InspectionImage).filter(InspectionImage.id == job.image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Associated image not found")
        
    building = db.query(Building).join(Inspection).filter(
        Inspection.id == image.inspection_id, 
        Building.organization_id == current_user.organization_id
    ).first()
    
    if not building:
        raise HTTPException(status_code=403, detail="Access denied")
        
    # Return job status
    return {
        "job_id": job.id,
        "status": job.status,
        "error_message": job.error_message,
        "started_at": job.started_at,
        "completed_at": job.completed_at
    }
