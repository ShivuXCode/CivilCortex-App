import sys
import json
from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from models.domain_models import User, Inspection

print("Initializing DB Tables...")
Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()

try:
    print("Checking for user...")
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(id=1, email="test@civilcortex.com", password_hash="dummy")
        db.add(user)
        db.commit()
        print("Created User 1.")

    print("Creating a test inspection...")
    insp = Inspection(
        title="Test Settlement",
        crack_type="Deep Foundation Settlement",
        severity="high",
        full_report_json={"health_score": 50, "recommendation": "Fix it!"},
        user_id=1
    )
    db.add(insp)
    db.commit()
    print("Saved inspection.")

    print("\n--- FETCHING INSPECTIONS ---")
    inspections = db.query(Inspection).all()
    for i in inspections:
        print(f"ID: {i.id} | Title: {i.title} | Severity: {i.severity} | Report: {json.dumps(i.full_report_json)}")
        
except Exception as e:
    print("Error:", e)
finally:
    db.close()
