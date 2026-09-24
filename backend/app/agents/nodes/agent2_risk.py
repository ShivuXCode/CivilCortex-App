from app.agents.state import AgentState
from app.services.risk_engine import RiskEngine
from app.core.logger import logger

def assess_risk(state: AgentState) -> dict:
    element_type = state.get("structure_type", "column")
    severity = state.get("severity", "low")
    
    # If severity is not a valid evaluated state, do not calculate risk
    valid_severities = ["low", "medium", "high", "critical", "none"]
    if not severity or severity.lower() not in valid_severities:
        logger.warning(f"Agent 2: Cannot calculate risk for invalid severity ({severity}).")
        return {
            "risk_score": None,
            "risk_level": "REQUIRES_REVIEW"
        }
    
    try:
        risk = RiskEngine.calculate_risk(element_type, None, severity)
        return {
            "risk_score": risk["score"],
            "risk_level": risk["level"]
        }
    except Exception as e:
        logger.error(f"Agent 2: Risk calculation failed: {e}")
        return {
            "risk_score": None,
            "risk_level": "REQUIRES_REVIEW"
        }
