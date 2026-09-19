from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="INSPECTOR") # INSPECTOR, ENGINEER, ADMIN
    organization_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    buildings = relationship("Building", back_populates="owner")
    inspections = relationship("Inspection", back_populates="inspector")

class Building(Base):
    __tablename__ = "buildings"
    id = Column(String, primary_key=True, default=generate_uuid)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    organization_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="buildings")
    floors = relationship("Floor", back_populates="building", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="building", cascade="all, delete-orphan")

class Floor(Base):
    __tablename__ = "floors"
    id = Column(String, primary_key=True, default=generate_uuid)
    building_id = Column(String, ForeignKey("buildings.id"), nullable=False)
    name = Column(String, nullable=False)
    level = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    building = relationship("Building", back_populates="floors")
    areas = relationship("Area", back_populates="floor", cascade="all, delete-orphan")

class Area(Base):
    __tablename__ = "areas"
    id = Column(String, primary_key=True, default=generate_uuid)
    floor_id = Column(String, ForeignKey("floors.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    floor = relationship("Floor", back_populates="areas")
    structural_elements = relationship("StructuralElement", back_populates="area", cascade="all, delete-orphan")

class StructuralElement(Base):
    __tablename__ = "structural_elements"
    id = Column(String, primary_key=True, default=generate_uuid)
    area_id = Column(String, ForeignKey("areas.id"), nullable=False)
    name = Column(String, nullable=False)
    element_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    area = relationship("Area", back_populates="structural_elements")
    defects = relationship("Defect", back_populates="structural_element", cascade="all, delete-orphan")
