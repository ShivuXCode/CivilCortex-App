import asyncio
from schemas.ai_contract import AnalysisInput, InspectionContext, ElementContext, ObservationContext, CVOutputContext, CVModelMetadata
from services.workflow_runner import run_analysis

req = AnalysisInput(
    inspection=InspectionContext(inspection_id="1"),
    element=ElementContext(element_id="1", element_type="Foundation"),
    observation=ObservationContext(crack_type="Deep Foundation Settlement", delay_risk="high"),
    cv_output=CVOutputContext(
        defect_type="crack", 
        confidence=0.9, 
        metadata=CVModelMetadata(model_name="test", model_version="1", model_status="PRODUCTION")
    )
)
try:
    print(run_analysis(req))
except Exception as e:
    import traceback
    traceback.print_exc()
