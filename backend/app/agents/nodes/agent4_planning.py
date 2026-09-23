from app.agents.state import AgentState

def plan_maintenance(state: AgentState) -> dict:
    severity = state.get("severity", "low").lower()
    
    if severity in ["high", "critical"]:
        action = "Immediate structural repair and reinforcement"
        workers = 5
        materials = ["Concrete", "Steel Rebar", "Epoxy"]
    elif severity == "medium":
        action = "Surface patching and sealing"
        workers = 2
        materials = ["Concrete Patch", "Sealant"]
    else:
        action = "Cosmetic touch-up and monitoring"
        workers = 1
        materials = ["Paint"]
        
    return {
        "maintenance_action": action,
        "required_workers": workers,
        "required_materials": materials
    }
