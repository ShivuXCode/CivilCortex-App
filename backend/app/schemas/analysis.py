from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnalysisCreate(BaseModel):
    title: str = "Untitled Detection"
    description: Optional[str] = None

class AnalysisUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class AnalysisResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    original_image_key: str
    masked_image_key: Optional[str] = None
    status: str
    report_text: Optional[str] = None
    severity_score: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
