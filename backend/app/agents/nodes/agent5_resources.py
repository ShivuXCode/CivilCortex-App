# No longer importing langchain LLM to guarantee deterministic behavior
from typing import List

# Deterministic lookup table for standard civil engineering maintenance actions
RESOURCE_DICTIONARY = {
    "epoxy injection": {
        "required_workers": 2,
        "required_materials": ["Epoxy Resin", "Injection Ports", "Surface Sealant", "Air Compressor"],
        "estimated_cost": "₹1,25,000 – ₹2,50,000"
    },
    "concrete reinforcement": {
        "required_workers": 4,
        "required_materials": ["Carbon Fiber Reinforced Polymer (CFRP)", "Epoxy Adhesive", "Scaffolding"],
        "estimated_cost": "₹6,50,000 – ₹12,00,000"
    },
    "foundation underpinning": {
        "required_workers": 6,
        "required_materials": ["High-strength Concrete", "Steel Piers", "Hydraulic Jacks", "Excavator"],
        "estimated_cost": "₹20,00,000 – ₹40,00,000"
    },
    "surface sealing": {
        "required_workers": 2,
        "required_materials": ["Polyurethane Sealant", "Wire Brushes", "Applicators"],
        "estimated_cost": "₹40,000 – ₹1,00,000"
    },
    "spalling repair": {
        "required_workers": 3,
        "required_materials": ["Repair Mortar", "Anti-corrosion Coating", "Rebar"],
        "estimated_cost": "₹1,60,000 – ₹4,00,000"
    }
}

# Fallback for unknown actions
DEFAULT_RESOURCES = {
    "required_workers": 3,
    "required_materials": ["Standard Assessment Tools", "General Repair Materials"],
    "estimated_cost": "Engineer Quote Required"
}

from app.core.config import settings
from app.demo.demo_engine import get_demo_scenario

def optimize_resources(state: dict) -> dict:
    # 0. Controlled Prototype / Demo Mode Execution
    if getattr(settings, "DEMO_MODE", False):
        scenario_id = state.get("scenario") or getattr(settings, "DEFAULT_DEMO_SCENARIO", "hairline_crack")
        sc = get_demo_scenario(scenario_id)
        return {
            "required_workers": sc["required_workers"],
            "required_materials": sc["required_materials"],
            "estimated_cost": sc["estimated_cost"]
        }

    # Handle edge case where Agent 4 didn't find a standard
    action = state.get("maintenance_action", "Surface Sealing").lower()
    
    if "manual engineer review" in action:
        return {
            "required_workers": 1,
            "required_materials": ["Inspection Equipment"],
            "estimated_cost": "TBD after manual review"
        }
    
    # Simple deterministic matching
    matched_resources = DEFAULT_RESOURCES
    for key, res in RESOURCE_DICTIONARY.items():
        if key in action:
            matched_resources = res
            break
            
    return matched_resources
