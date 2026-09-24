from sqlalchemy import Column, String, DateTime, Text, Float
from datetime import datetime
import uuid

from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False, default="Untitled Detection")
    description = Column(Text, nullable=True)
    
    # Storage keys (MinIO)
    original_image_key = Column(String, nullable=False)
    masked_image_key = Column(String, nullable=True)
    
    # ML Results
    status = Column(String, nullable=False, default="PROCESSING") # PROCESSING, COMPLETED, FAILED
    report_text = Column(Text, nullable=True)
    severity_score = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
