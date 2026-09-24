from app.agents.state import AgentState

def assess_condition(state: AgentState) -> dict:
    # 1. Extract CV metrics from state
    mask_coverage = state.get("mask_coverage")
    largest_component_area = state.get("largest_component_area")
    crack_detected = state.get("crack_detected", False)
    crack_type = state.get("crack_type", "none")
    
    # 2. If no defect was detected, return healthy state
    if not crack_detected or crack_type.lower() == "none":
        return {
            "severity": "none",
            "condition": "No Visible Damage",
            "health_score": 100
        }
        
    # 3. If evidence is missing, we must NOT hallucinate severity. Return explicit review state.
    if mask_coverage is None and largest_component_area is None:
        return {
            "severity": "REQUIRES_REVIEW",
            "condition": "REQUIRES_REVIEW",
            "health_score": 0
        }
        
    # Safely get values, defaulting to 0 if one metric is missing but the other is present
    cov = mask_coverage if mask_coverage is not None else 0.0
    area = largest_component_area if largest_component_area is not None else 0
    
    # 4. Evaluate engineering severity based on deterministic 384x384 geometric thresholds
    if cov > 0.20 or area > 20000:
        severity = "critical"
        condition = "Critical Failure (Heuristic - Requires Review)"
        health = 10
    elif cov > 0.10 or area > 10000:
        severity = "high"
        condition = "Severe Damage (Heuristic - Requires Review)"
        health = 30
    elif cov > 0.02 or area > 2000:
        severity = "medium"
        condition = "Moderate Wear (Heuristic - Requires Review)"
        health = 60
    else:
        severity = "low"
        condition = "Minor Wear (Heuristic - Requires Review)"
        health = 90
        
    return {
        "severity": severity,
        "condition": condition,
        "health_score": health
    }
