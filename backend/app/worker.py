import os
from datetime import datetime
from redis import Redis
from rq import Queue
import sys

# Ensure backend directory is in the python path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.analysis import AnalysisJob
from app.models.inspection import InspectionImage, Inspection
from app.services.analysis_service import AnalysisService
from app.core.exceptions import CivilCortexError
from app.core.logger import logger, job_id_var

# Configure Redis Connection
redis_conn = Redis.from_url(settings.REDIS_URL)

# Configure Queues
analysis_queue = Queue('analysis', connection=redis_conn)

def run_analysis_job(job_id: str, test_db=None):
    """
    Background task to run the AI analysis workflow via RQ.
    """
    job_id_var.set(job_id)
    logger.info(f"Worker picked up job {job_id}")
    
    db = test_db if test_db else SessionLocal()
    try:
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            logger.error(f"AnalysisJob {job_id} not found in database.")
            return
            
        # Idempotency check: if job is already processing or completed, skip it
        if job.status in ["PROCESSING", "COMPLETED"]:
            logger.info(f"AnalysisJob {job_id} is already in state {job.status}. Skipping duplicate execution.")
            return
            
        # Transition to PROCESSING
        job.status = "PROCESSING"
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Verify related image exists
        image = db.query(InspectionImage).filter(InspectionImage.id == job.image_id).first()
        if not image:
            job.status = "FAILED"
            job.error_message = "NOT_FOUND"
            job.completed_at = datetime.utcnow()
            db.commit()
            return
            
        # Fetch inspection ID (needed by AnalysisService)
        inspection = db.query(Inspection).filter(Inspection.id == image.inspection_id).first()
        if not inspection:
            job.status = "FAILED"
            job.error_message = "NOT_FOUND"
            job.completed_at = datetime.utcnow()
            db.commit()
            return
        
        # Execute the AnalysisService
        try:
            # We use the existing synchronous logic from Phase 6, but in a background worker context
            # It already persists the result internally.
            result = AnalysisService.run_synchronous_analysis(
                image_id=str(image.id),
                inspection_id=str(inspection.id),
                db=db,
                user_id=inspection.inspector_id
            )
            
            # Transition to COMPLETED
            job.status = "COMPLETED"
            job.completed_at = datetime.utcnow()
            db.commit()
            logger.info(f"Job {job_id} completed successfully.")
            
        except CivilCortexError as e:
            logger.error(f"Domain error during analysis execution for job {job_id}: {e.code} - {e.message}")
            job.status = "FAILED"
            job.error_message = e.code
            job.completed_at = datetime.utcnow()
            db.commit()
        except Exception as e:
            logger.error(f"Unhandled error during analysis execution for job {job_id}: {e}", exc_info=True)
            job.status = "FAILED"
            job.error_message = "INTERNAL_ERROR"
            job.completed_at = datetime.utcnow()
            db.commit()
            
    finally:
        if not test_db:
            db.close()
        job_id_var.set("")
