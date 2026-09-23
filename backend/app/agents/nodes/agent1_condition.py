from app.agents.state import AgentState

def assess_condition(state: AgentState) -> dict:
    severity = state.get("severity", "low").lower()
    
    if severity == "critical":
        condition = "Critical Failure"
        health = 10
    elif severity == "high":
        condition = "Severe Damage"
        health = 30
    elif severity == "medium":
        condition = "Moderate Wear"
        health = 60
    else:
        condition = "Minor Wear"
        health = 90
        
    return {
        "condition": condition,
        "health_score": health
    }
