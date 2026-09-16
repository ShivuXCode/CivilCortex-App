import sys
import json
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.hierarchy import User, Building, Floor, Area, StructuralElement
from app.models.inspection import Inspection, InspectionImage
from app.models.defect import Defect, CrackObservation, Assessment
from app.models.analysis import AnalysisJob

def test_db():
    print("Initializing DB Tables...")
    # Base.metadata.create_all(bind=engine) # Should be done by alembic

    db: Session = SessionLocal()

    try:
        print("Checking for user...")
        user = db.query(User).filter(User.email == "test@civilcortex.com").first()
        if not user:
            user = User(email="test@civilcortex.com", hashed_password="dummy")
            db.add(user)
            db.commit()
            print("Created User.")

        print("Creating a test building and hierarchy...")
        building = db.query(Building).first()
        if not building:
            building = Building(name="Test Building", owner_id=user.id)
            db.add(building)
            db.commit()
        
        floor = db.query(Floor).first()
        if not floor:
            floor = Floor(building_id=building.id, name="Ground Floor", level=1)
            db.add(floor)
            db.commit()

        area = db.query(Area).first()
        if not area:
            area = Area(floor_id=floor.id, name="North Wing")
            db.add(area)
            db.commit()

        element = db.query(StructuralElement).first()
        if not element:
            element = StructuralElement(area_id=area.id, name="North Wall", element_type="Wall")
            db.add(element)
            db.commit()

        print("Creating a test inspection...")
        insp = Inspection(
            building_id=building.id,
            inspector_id=user.id,
            notes="Test notes"
        )
        db.add(insp)
        db.commit()

        print("Creating inspection image...")
        img = InspectionImage(
            inspection_id=insp.id,
            file_path="/tmp/test.jpg",
            original_filename="test.jpg",
            mime_type="image/jpeg",
            file_size=1024
        )
        db.add(img)
        db.commit()

        print("Creating analysis job...")
        job = AnalysisJob(
            image_id=img.id,
            status="QUEUED"
        )
        db.add(job)
        db.commit()

        print("Creating defect, observation and assessment...")
        defect = Defect(
            structural_element_id=element.id,
            defect_type="crack",
            status="CANDIDATE"
        )
        db.add(defect)
        db.commit()

        obs = CrackObservation(
            defect_id=defect.id,
            inspection_id=insp.id,
            image_id=img.id
        )
        db.add(obs)
        db.commit()

        assessment = Assessment(
            observation_id=obs.id,
            severity="high",
            risk="REQUIRES_REVIEW",
            risk_score=85,
            priority="P1",
            rag_context="According to ACI 318...",
            repair_recommendation="Immediate repair using epoxy injection."
        )
        db.add(assessment)
        db.commit()
        print("Saved assessment with LangGraph fields.")

        print("\n--- FETCHING ASSESSMENT ---")
        fetched_assessment = db.query(Assessment).filter(Assessment.id == assessment.id).first()
        print(f"ID: {fetched_assessment.id} | Severity: {fetched_assessment.severity} | Risk Score: {fetched_assessment.risk_score} | Priority: {fetched_assessment.priority} | RAG Context: {fetched_assessment.rag_context[:15]}... | Recommendation: {fetched_assessment.repair_recommendation[:15]}...")
        
        print("\n--- FETCHING ANALYSIS JOB ---")
        fetched_job = db.query(AnalysisJob).filter(AnalysisJob.image_id == img.id).first()
        print(f"Job ID: {fetched_job.id} | Status: {fetched_job.status}")

        print("Test passed successfully.")
        
    except Exception as e:
        print("Error:", e)
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    test_db()
