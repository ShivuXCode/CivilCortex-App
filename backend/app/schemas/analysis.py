from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AnalysisJobResponse(BaseModel):
    job_id: str
    status: str
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
