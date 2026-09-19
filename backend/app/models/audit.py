from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
import uuid

from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True) # e.g., "ASSESSMENT"
    entity_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False) # e.g., "UPDATE"
    previous_state = Column(JSONB, nullable=True)
    new_state = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
