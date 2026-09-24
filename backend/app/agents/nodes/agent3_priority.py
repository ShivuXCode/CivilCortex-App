from app.agents.state import AgentState
from app.services.priority_engine import PriorityEngine
from app.core.logger import logger

def assess_priority(state: AgentState) -> dict:
    risk_level = state.get("risk_level", "Medium")
    severity = state.get("severity", "low")
    
    # If severity or risk_level are not valid, do not fabricate a priority
    valid_severities = ["low", "medium", "high", "critical", "none"]
    if not severity or severity.lower() not in valid_severities:
        logger.warning(f"Agent 3: Cannot calculate priority for invalid severity ({severity}).")
        return {
            "priority": "REQUIRES_REVIEW",
            "days": None
        }
    
    if risk_level == "REQUIRES_REVIEW":
        logger.warning("Agent 3: Cannot calculate priority with REQUIRES_REVIEW risk level.")
        return {
            "priority": "REQUIRES_REVIEW",
            "days": None
        }
    
    try:
        prio = PriorityEngine.calculate_priority(risk_level, severity)
        return {
            "priority": prio["level"],
            "days": prio["max_days"]
        }
    except Exception as e:
        logger.error(f"Agent 3: Priority calculation failed: {e}")
        return {
            "priority": "REQUIRES_REVIEW",
            "days": None
        }
