"""
CivilCortex - Centralized Demo Scenarios Definition
Deterministic inspection profiles for presentation and prototype demonstration.
"""

from typing import Dict, Any

DEMO_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "no_crack": {
        "scenario_id": "no_crack",
        "title": "No Crack (Clean Concrete)",
        "crack_detected": False,
        "crack_probability": 0.03,
        "crack_type": "None",
        "severity": "low",
        "health_score": 100,
        "condition": "Excellent",
        "risk_score": 5.0,
        "risk_level": "Low",
        "priority": "Routine",
        "days": 30,
        "recommended_action": "No immediate repair required. Continue periodic inspection.",
        "repair_method": "Surface Cleaning & Periodic Monitoring",
        "required_materials": ["None"],
        "required_workers": 0,
        "estimated_cost": "₹0",
        "rag_context": (
            "Source: IS 456:2000 (Plain and Reinforced Concrete - Code of Practice), Section 35.3.2:\n"
            "Surface condition is evaluated as structurally intact. No cracks or micro-fissures exceeding "
            "allowable tolerances (0.1 mm) detected. Continue routine periodic structural monitoring under "
            "scheduled facility maintenance protocol."
        )
    },
    "hairline_crack": {
        "scenario_id": "hairline_crack",
        "title": "Hairline Crack (Minor)",
        "crack_detected": True,
        "crack_probability": 0.87,
        "crack_type": "Hairline Crack",
        "severity": "low",
        "health_score": 88,
        "condition": "Fair",
        "risk_score": 32.0,
        "risk_level": "Medium",
        "priority": "Inspection / repair within 30 days",
        "days": 30,
        "recommended_action": "Seal the crack and monitor for propagation.",
        "repair_method": "Low-Pressure Polyurethane Surface Sealing",
        "required_materials": [
            "Low-Viscosity Crack Sealant",
            "Surface Cleaning Brushes",
            "Polymer Injection Ports"
        ],
        "required_workers": 1,
        "estimated_cost": "₹2,500 – ₹5,000",
        "rag_context": (
            "Source: ACI 224.1R-07 (Causes, Evaluation, and Repair of Cracks in Concrete Structures), Section 3.2:\n"
            "For non-structural hairline cracks (<0.3 mm width), surface sealing using low-viscosity elastomeric "
            "or epoxy sealants is recommended to prevent moisture and chloride ingress, arresting rebar corrosion. "
            "Remediation must be scheduled within 30 days."
        )
    },
    "moderate_crack": {
        "scenario_id": "moderate_crack",
        "title": "Moderate Structural Crack",
        "crack_detected": True,
        "crack_probability": 0.94,
        "crack_type": "Structural Crack",
        "severity": "medium",
        "health_score": 68,
        "condition": "Poor",
        "risk_score": 68.0,
        "risk_level": "High",
        "priority": "Repair within 7 days",
        "days": 7,
        "recommended_action": "Conduct detailed structural inspection and repair the affected region.",
        "repair_method": "Pressure Epoxy Injection & Polymer-Modified Mortar Patching",
        "required_materials": [
            "High-Strength Structural Epoxy Resin",
            "Polymer-Modified Repair Mortar",
            "Injection Ports & Caps",
            "Surface Degreaser & Primer"
        ],
        "required_workers": 3,
        "estimated_cost": "₹10,000 – ₹25,000",
        "rag_context": (
            "Source: ACI 546R-14 (Guide to Concrete Repair) & IRC:SP:40, Clause 4.3:\n"
            "Active structural cracks between 0.3 mm and 1.5 mm require pressure-injected structural epoxy "
            "to restore monolithic flexural strength. Surface spalls must be primed and patched with polymer-modified "
            "mortar within 7 days of inspection."
        )
    },
    "severe_crack": {
        "scenario_id": "severe_crack",
        "title": "Severe Structural Crack",
        "crack_detected": True,
        "crack_probability": 0.98,
        "crack_type": "Severe Structural Crack",
        "severity": "high",
        "health_score": 35,
        "condition": "Critical",
        "risk_score": 92.0,
        "risk_level": "Critical",
        "priority": "Immediate inspection",
        "days": 1,
        "recommended_action": "Restrict access if necessary and conduct immediate structural assessment.",
        "repair_method": "Section Shoring, High-Pressure Epoxy Grouting & CFRP Composite Reinforcement",
        "required_materials": [
            "Carbon Fiber Reinforced Polymer (CFRP) Sheets",
            "Structural Epoxy Saturant Adhesive",
            "Heavy-Duty Hydraulic Shoring Props",
            "Micro-Concrete Grouting Mortar"
        ],
        "required_workers": 5,
        "estimated_cost": "₹25,000 – ₹75,000",
        "rag_context": (
            "Source: FHWA-HRT-14-041 & IS 13920:2016 (Ductile Design & Structural Assessment):\n"
            "Severe shear or flexural cracks (>2.0 mm) with evidence of structural displacement necessitate immediate "
            "temporary mechanical shoring and load redistribution. Remediation requires composite CFRP wrapping or "
            "steel plate jacketing supervised by a licensed structural engineer within 24 hours."
        )
    }
}

DEFAULT_SCENARIO_ID = "hairline_crack"
