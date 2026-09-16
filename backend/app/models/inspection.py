from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class Inspection(Base):
    __tablename__ = "inspections"
    id = Column(String, primary_key=True, default=generate_uuid)
    building_id = Column(String, ForeignKey("buildings.id"), nullable=False)
    inspector_id = Column(String, ForeignKey("users.id"), nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    building = relationship("Building", back_populates="inspections")
    inspector = relationship("User", back_populates="inspections")
    images = relationship("InspectionImage", back_populates="inspection", cascade="all, delete-orphan")
    observations = relationship("CrackObservation", back_populates="inspection", cascade="all, delete-orphan")

class InspectionImage(Base):
    __tablename__ = "inspection_images"
    id = Column(String, primary_key=True, default=generate_uuid)
    inspection_id = Column(String, ForeignKey("inspections.id"), nullable=False)
    object_key = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    inspection = relationship("Inspection", back_populates="images")
    observations = relationship("CrackObservation", back_populates="image")
    analysis_job = relationship("AnalysisJob", back_populates="image", uselist=False, cascade="all, delete-orphan")
