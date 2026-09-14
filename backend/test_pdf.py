import sys
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.domain_models import Inspection
from services.pdf_generator import generate_inspection_pdf

db: Session = SessionLocal()
insp = db.query(Inspection).first()
if insp:
    print(f"Generating PDF for Inspection ID: {insp.id}")
    pdf_bytes = generate_inspection_pdf(insp)
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_bytes)
    print(f"Success! PDF size: {len(pdf_bytes)} bytes")
else:
    print("No inspections found in DB to test.")
db.close()
