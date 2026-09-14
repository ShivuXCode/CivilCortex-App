from core.config import settings
from demo.demo_engine import get_demo_scenario

def assess_risk(state: dict) -> dict:
    # 0. Controlled Prototype / Demo Mode Execution
    if getattr(settings, "DEMO_MODE", False):
        scenario_id = state.get("scenario") or getattr(settings, "DEFAULT_DEMO_SCENARIO", "hairline_crack")
        sc = get_demo_scenario(scenario_id)
        return {
            "risk_score": sc["risk_score"],
            "risk_level": sc["risk_level"],
            "is_load_bearing": state.get("is_load_bearing", True),
            "structure_type": state.get("structure_type", "tunnel")
        }

    health_score = state.get("health_score", 100)
    
    # Industry-level structural context replacing generic safety metrics
    is_load_bearing = state.get("is_load_bearing", True)
    structure_type = state.get("structure_type", "tunnel").lower()
    
    # Dynamic weighting based on structure type and load bearing status
    # Base risk is inverse of health score
    base_risk = 100 - health_score
    
    # Determine risk multiplier based on structure criticality
    if structure_type in ["bridge", "tunnel", "dam"]:
        criticality_multiplier = 1.2
    elif structure_type in ["foundation", "retaining_wall"]:
        criticality_multiplier = 1.0
    else:
        criticality_multiplier = 0.8
        
    # Load bearing elements pose significantly higher risk of catastrophic failure
    load_multiplier = 1.5 if is_load_bearing else 0.7
    
    # Calculate final weighted risk score (capped at 100)
    risk_score = min(100.0, base_risk * criticality_multiplier * load_multiplier)
    
    # ISO-aligned risk thresholds
    if risk_score >= 75:
        risk_level = "High"
    elif risk_score >= 40:
        risk_level = "Medium"
    else:
        risk_level = "Low"
        
    return {
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "is_load_bearing": is_load_bearing,
        "structure_type": structure_type
    }
