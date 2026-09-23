from sqlalchemy import Column, String, Float
from app.db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Material(Base):
    __tablename__ = "materials"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    unit_rate = Column(Float, nullable=False)

class LaborRate(Base):
    __tablename__ = "labor_rates"
    id = Column(String, primary_key=True, default=generate_uuid)
    category = Column(String, nullable=False, unique=True)
    daily_rate = Column(Float, nullable=False)
