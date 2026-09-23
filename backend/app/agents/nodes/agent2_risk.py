from app.agents.state import AgentState
from app.services.risk_engine import RiskEngine

def assess_risk(state: AgentState) -> dict:
    element_type = state.get("structure_type", "column")
    severity = state.get("severity", "low")
    
    try:
        risk = RiskEngine.calculate_risk(element_type, None, severity)
        return {
            "risk_score": risk["score"],
            "risk_level": risk["level"]
        }
    except Exception:
        return {
            "risk_score": 50.0,
            "risk_level": "Medium"
        }
