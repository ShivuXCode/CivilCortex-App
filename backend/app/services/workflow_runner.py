from app.agents.graph import app as workflow_app
from app.schemas.ai_contract import AnalysisInput, AnalysisResult, PlanningInformation
from app.core.exceptions import LLMError
from app.core.logger import logger
import time

def run_analysis(input_data: AnalysisInput) -> AnalysisResult:
    # 1. Map AnalysisInput to AgentState
    initial_state = {
        "crack_type": input_data.observation.crack_type,
        "severity": "unknown", # Will be evaluated by LLM Vision
        "delay_risk": input_data.observation.delay_risk,
        "is_load_bearing": input_data.element.is_load_bearing,
        "structure_type": input_data.element.element_type,
        "image_bytes": input_data.image_bytes,
        "rag_evidence": [ev.model_dump() for ev in input_data.rag_evidence] if input_data.rag_evidence else None,
        
        # Inject CV data into LangGraph if possible (LangGraph will populate it, but we can seed it)
        "crack_detected": input_data.cv_output.defect_type != "none",
        "crack_probability": input_data.cv_output.confidence,
        "mask_coverage": input_data.cv_output.mask_coverage,
        "component_count": input_data.cv_output.component_count,
        "largest_component_area": input_data.cv_output.largest_component_area,
    }
    
    # 2. Execute Graph
    start_time = time.time()
    try:
        final_state = workflow_app.invoke(initial_state)
    except Exception as e:
        logger.error(f"LangGraph execution failed: {e}")
        raise LLMError(f"LangGraph execution failed: {e}")
    end_time = time.time()
    
    # 3. Map AgentState back to AnalysisResult
    planning = PlanningInformation(
        maintenance_action=final_state.get("maintenance_action"),
        required_workers=final_state.get("required_workers"),
        required_materials=final_state.get("required_materials"),
        estimated_cost=final_state.get("estimated_cost")
    )
    
    rag_available = bool(input_data.rag_evidence)
    if not rag_available:
        logger.warning(
            "event=rag_evidence status=absent "
            "RAG database returned no engineering standards evidence. "
            "The AI report will be generated without standards citations and may be less reliable."
        )

    return AnalysisResult(
        defect_detected=final_state.get("crack_detected", input_data.cv_output.defect_type != "none"),
        defect_probability=final_state.get("crack_probability", input_data.cv_output.confidence),
        condition=final_state.get("condition"),
        severity=final_state.get("severity"),
        health_score=final_state.get("health_score"),
        risk_score=final_state.get("risk_score"),
        risk_level=final_state.get("risk_level"),
        priority=final_state.get("priority"),
        max_days=final_state.get("days"),
        recommendation=final_state.get("recommendation"),
        executive_report=None,
        planning=planning,
        rag_evidence=input_data.rag_evidence,
        rag_evidence_available=rag_available,
        processing_metadata={"processing_time_ms": int((end_time - start_time) * 1000)},
        error=None
    )
