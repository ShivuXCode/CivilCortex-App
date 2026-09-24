from app.services.workflow_runner import run_analysis
from app.schemas.ai_contract import AnalysisInput, ObservationContext, ElementContext, CVOutputContext, InspectionContext
from app.schemas.ai_contract import RAGEvidence, CVModelMetadata
import sys

input_data = AnalysisInput(
    inspection=InspectionContext(inspection_id="1", title="Test"),
    element=ElementContext(element_id="1", element_type="Bridge Deck", is_load_bearing=True),
    observation=ObservationContext(crack_type="crack", delay_risk="unknown"),
    cv_output=CVOutputContext(
        defect_type="crack",
        confidence=0.9,
        mask_coverage=0.01,
        component_count=1,
        largest_component_area=500,
        metadata=CVModelMetadata(model_name="test", model_version="1", model_status="test")
    ),
    image_bytes=b"dummy",
    rag_evidence=[]
)

result = run_analysis(input_data)
print("Result Severity:", result.severity)
print("Result Condition:", result.condition)
print("Result Recommendation:", result.recommendation)
print("Result Maintenance Action:", result.planning.maintenance_action)
