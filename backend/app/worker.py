import os
import sys
from datetime import datetime, timezone
from redis import Redis
from rq import Queue

# Ensure backend directory is in the python path for absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.analysis import Analysis
from app.services.analysis_service import AnalysisService
from app.core.exceptions import CivilCortexError
from app.core.logger import logger, job_id_var

# Configure Redis Connection
redis_conn = None
analysis_queue = None
if settings.REDIS_URL:
    try:
        redis_conn = Redis.from_url(settings.REDIS_URL)
        analysis_queue = Queue('analysis', connection=redis_conn)
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}. Worker queue will be disabled.")

def run_analysis_job(analysis_id: str, test_db=None):
    job_id_var.set(analysis_id)
    logger.info(f"Worker picked up analysis {analysis_id}")
    
    db = test_db if test_db else SessionLocal()
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found in database.")
            return
            
        if analysis.status in ["COMPLETED"]:
            logger.info(f"Analysis {analysis_id} is already COMPLETED. Skipping.")
            return
            
        analysis.status = "PROCESSING"
        db.commit()
        
        try:
            # Run the ML & AI Analysis pipeline
            AnalysisService.run_analysis_pipeline(analysis, db)
            
            analysis.status = "COMPLETED"
            analysis.completed_at = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Analysis {analysis_id} completed successfully.")
            
        except CivilCortexError as e:
            logger.error(f"Domain error during analysis {analysis_id}: {e.code} - {e.message}")
            analysis.status = "FAILED"
            analysis.error_message = e.message
            analysis.completed_at = datetime.now(timezone.utc)
            db.commit()
        except Exception as e:
            logger.error(f"Unexpected error during analysis {analysis_id}: {str(e)}")
            analysis.status = "FAILED"
            analysis.error_message = "INTERNAL_ERROR"
            analysis.completed_at = datetime.now(timezone.utc)
            db.commit()
            
    finally:
        if not test_db:
            db.close()
        job_id_var.set("")

def reap_stale_jobs():
    from datetime import timedelta
    db = SessionLocal()
    try:
        ten_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
        stale_jobs = db.query(Analysis).filter(
            Analysis.status == "PROCESSING",
            Analysis.created_at < ten_minutes_ago
        ).all()
        
        count = 0
        for job in stale_jobs:
            job.status = "FAILED"
            job.error_message = "WORKER_TIMEOUT"
            job.completed_at = datetime.now(timezone.utc)
            count += 1
            
        if count > 0:
            db.commit()
            logger.info(f"Reaped {count} stale analyses.")
    except Exception as e:
        logger.error(f"Error while reaping stale analyses: {e}", exc_info=True)
    finally:
        db.close()
