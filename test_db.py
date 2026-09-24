import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from app.db.session import SessionLocal
from app.models.defect import Assessment

db = SessionLocal()
a = db.query(Assessment).filter(Assessment.rag_context.isnot(None)).first()
if a:
    print(repr(a.rag_context))
