import sys
import os
sys.path.insert(0, os.path.abspath('backend'))
from app.services.rag_service import rag_service
query = "Standards, repair guidelines, and safety assessment for crack in Bridge Deck"
evidence = rag_service.retrieve_evidence(query)
print(f"Evidence count: {len(evidence)}")
for e in evidence:
    print(e.text)
