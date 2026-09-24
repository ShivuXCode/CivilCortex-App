import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisResponse
from app.services.storage_service import storage_service

router = APIRouter()

@router.post("", response_model=AnalysisResponse)
async def create_analysis(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Enqueue standard validation
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(400, "Only JPEG and PNG images are supported.")
        
    ext = ".jpg" if "jpeg" in file.content_type else ".png"
    object_key = f"analyses/{uuid.uuid4()}{ext}"
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    storage_service.upload_file(file.file, object_key, file_size, file.content_type)
    
    # Create DB Record
    analysis = Analysis(
        title=title,
        description=description,
        original_image_key=object_key,
        status="PROCESSING"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    from app.worker import run_analysis_job
    background_tasks.add_task(run_analysis_job, str(analysis.id))
        
    return analysis

@router.get("", response_model=List[AnalysisResponse])
def get_all_analyses(db: Session = Depends(get_db)):
    return db.query(Analysis).order_by(Analysis.created_at.desc()).all()

@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(404, "Analysis not found")
    return analysis

@router.delete("/{analysis_id}")
def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(404, "Analysis not found")
        
    try:
        storage_service.delete_file(analysis.original_image_key)
        if analysis.masked_image_key:
            storage_service.delete_file(analysis.masked_image_key)
    except Exception:
        pass # Ignore storage deletion errors
        
    db.delete(analysis)
    db.commit()
    return {"status": "deleted"}

from fastapi.responses import StreamingResponse
import io

@router.get("/image/{object_key:path}")
def get_image(object_key: str):
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        try:
            storage_service.download_file(object_key, tmp.name)
            with open(tmp.name, "rb") as f:
                content = f.read()
            return StreamingResponse(io.BytesIO(content), media_type="image/jpeg")
        except Exception as e:
            raise HTTPException(404, "Image not found")
        finally:
            if os.path.exists(tmp.name):
                os.remove(tmp.name)
