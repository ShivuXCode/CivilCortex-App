import json
from dotenv import load_dotenv
load_dotenv()
from schemas.ai_contract import AnalysisInput, InspectionContext, ElementContext, ObservationContext, CVOutputContext, CVModelMetadata
from services.workflow_runner import run_analysis

request = AnalysisInput(
    inspection=InspectionContext(inspection_id="1"),
    element=ElementContext(element_id="1", element_type="Foundation"),
    observation=ObservationContext(crack_type="Deep Foundation Settlement", delay_risk="high"),
    cv_output=CVOutputContext(
        defect_type="crack", 
        confidence=0.9, 
        metadata=CVModelMetadata(model_name="test", model_version="1", model_status="PRODUCTION")
    )
)

result = run_analysis(request)

print("="*50)
print("AGENT 4: RETRIEVED RAG CONTEXT (TRUTH)")
print("="*50)
print(result.rag_context)
print("\n" + "="*50)
print("AGENT 6: FINAL LLM RECOMMENDATION")
print("="*50)
print(result.recommendation)
print("="*50)
