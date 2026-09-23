from app.agents.state import AgentState
from app.services.priority_engine import PriorityEngine

def assess_priority(state: AgentState) -> dict:
    risk_level = state.get("risk_level", "Medium")
    severity = state.get("severity", "low")
    
    try:
        prio = PriorityEngine.calculate_priority(risk_level, severity)
        return {
            "priority": prio["level"],
            "days": prio["max_days"]
        }
    except Exception:
        return {
            "priority": "High Priority",
            "days": 90
        }
