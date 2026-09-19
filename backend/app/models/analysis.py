from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    id = Column(String, primary_key=True, default=generate_uuid)
    image_id = Column(String, ForeignKey("inspection_images.id"), nullable=False, unique=True)
    status = Column(String, nullable=False, default="QUEUED", index=True) # QUEUED, PROCESSING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    image = relationship("InspectionImage", back_populates="analysis_job")
