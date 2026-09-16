from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class Defect(Base):
    __tablename__ = "defects"
    id = Column(String, primary_key=True, default=generate_uuid)
    structural_element_id = Column(String, ForeignKey("structural_elements.id"), nullable=True)
    defect_type = Column(String, nullable=False)  # "crack", "spalling", "efflorescence"
    status = Column(String, nullable=False, default="CANDIDATE") # CANDIDATE, MONITORED, REPAIRED, DISMISSED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    structural_element = relationship("StructuralElement", back_populates="defects")
    observations = relationship("CrackObservation", back_populates="defect", cascade="all, delete-orphan")

class CrackObservation(Base):
    __tablename__ = "crack_observations"
    id = Column(String, primary_key=True, default=generate_uuid)
    defect_id = Column(String, ForeignKey("defects.id"), nullable=False)
    inspection_id = Column(String, ForeignKey("inspections.id"), nullable=False)
    image_id = Column(String, ForeignKey("inspection_images.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    defect = relationship("Defect", back_populates="observations")
    inspection = relationship("Inspection", back_populates="observations")
    image = relationship("InspectionImage", back_populates="observations")
    assessment = relationship("Assessment", back_populates="observation", uselist=False, cascade="all, delete-orphan")

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(String, primary_key=True, default=generate_uuid)
    observation_id = Column(String, ForeignKey("crack_observations.id"), nullable=False, unique=True)
    severity = Column(String, nullable=False, default="UNKNOWN") # LOW, MODERATE, HIGH, CRITICAL, UNKNOWN
    risk = Column(String, nullable=False, default="REQUIRES_REVIEW") # LOW, MODERATE, HIGH, REQUIRES_ENGINEER_REVIEW, REQUIRES_REVIEW
    risk_score = Column(Integer, nullable=True)
    priority = Column(String, nullable=True)
    rag_context = Column(String, nullable=True)
    repair_recommendation = Column(String, nullable=True)
    llm_report = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    observation = relationship("CrackObservation", back_populates="assessment")
