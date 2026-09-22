def assess_priority(state: dict) -> dict:
    risk_level = state.get("risk_level", "Low")
    delay_risk = state.get("delay_risk", "low").lower()
    
    # Priority mapping aligned with FHWA (Federal Highway Administration) 
    # and ISO 13822 standards for concrete structures (bridges, walls, pavements).
    if risk_level == "High" or delay_risk == "high":
        priority = "Immediate (Emergency)"
        # Standard: Immediate closure or shoring required within 24 hours
        days = 1
    elif risk_level == "Medium":
        priority = "Urgent (Priority Repair)"
        # Standard: Must be addressed in the next maintenance cycle or within 7 days
        days = 7
    else:
        priority = "Routine (Monitor)"
        # Standard: Standard observation, schedule for routine maintenance
        days = 30
        
    return {
        "priority": priority,
        "days": days
    }
