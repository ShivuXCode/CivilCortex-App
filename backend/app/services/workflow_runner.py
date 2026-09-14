from agents.graph import app as workflow_app
from schemas.request_models import MaintenanceRequest

def run_analysis(request_data: MaintenanceRequest) -> dict:
    # Initialize the LangGraph state
    initial_state = {
        "crack_type": request_data.crack_type,
        "severity": request_data.severity,
        "helmet_compliance": 1.0,
        "delay_risk": request_data.delay_risk,
        "is_load_bearing": request_data.is_load_bearing,
        "structure_type": request_data.structure_type,
        "image_bytes": request_data.image_bytes,
        "scenario": getattr(request_data, "scenario", "hairline_crack")
    }
    
    # Execute the compiled workflow
    final_state = workflow_app.invoke(initial_state)
    return final_state
