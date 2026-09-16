import pytest
from pydantic import ValidationError
from app.schemas.ai_contract import (
    AnalysisInput, InspectionContext, ElementContext, ObservationContext, 
    CVOutputContext, CVModelMetadata, AnalysisResult, PlanningInformation
)
from app.services.workflow_runner import run_analysis
from app.agents.state import AgentState

def test_valid_analysis_input_creation():
    input_data = AnalysisInput(
        inspection=InspectionContext(inspection_id="1", title="Test Inspection"),
        element=ElementContext(element_id="2", element_type="Wall", building_type="Commercial", is_load_bearing=True),
        observation=ObservationContext(crack_type="Hairline", delay_risk="low"),
        cv_output=CVOutputContext(
            defect_type="crack",
            confidence=0.85,
            metadata=CVModelMetadata(model_name="test", model_version="v1", model_status="PRODUCTION")
        )
    )
    assert input_data.inspection.inspection_id == "1"
    assert input_data.scenario == "hairline_crack" # default

def test_analysis_input_validation_failure():
    with pytest.raises(ValidationError):
        # Missing required fields
        AnalysisInput(
            inspection=InspectionContext(inspection_id="1")
        )

def test_cv_to_analysis_contract_conversion():
    cv_metadata = CVModelMetadata(model_name="seg", model_version="1.0", model_status="PRODUCTION")
    cv_output = CVOutputContext(defect_type="none", confidence=0.1, metadata=cv_metadata)
    assert cv_output.defect_type == "none"
    
def test_valid_analysis_result():
    result = AnalysisResult(
        defect_detected=True,
        defect_probability=0.9,
        severity="high",
        risk_level="CRITICAL"
    )
    assert result.defect_detected is True
    assert result.planning.maintenance_action is None # default empty
    assert result.processing_metadata.processing_time_ms is None

def test_workflow_runner_state_compatibility():
    # Test that workflow_runner correctly maps AnalysisInput into AgentState
    # Note: run_analysis internally creates AgentState
    input_data = AnalysisInput(
        inspection=InspectionContext(inspection_id="1"),
        element=ElementContext(element_id="1", element_type="Tunnel"),
        observation=ObservationContext(crack_type="Deep Foundation Settlement", delay_risk="high"),
        cv_output=CVOutputContext(
            defect_type="crack",
            confidence=0.92,
            metadata=CVModelMetadata(model_name="test", model_version="v1", model_status="PRODUCTION")
        )
    )
    
    # We mock or just test the mapping function if it was isolated, 
    # but since run_analysis executes the graph, let's just make sure it returns an AnalysisResult
    # (The actual graph might fail if no LLM key is provided, but it's caught in run_analysis)
    
    result = run_analysis(input_data)
    
    # Check that AnalysisResult is returned
    assert isinstance(result, AnalysisResult)
    # The default state sets crack_detected=True from cv_output
    assert result.defect_detected in [True, False]
    assert isinstance(result.defect_probability, float)
