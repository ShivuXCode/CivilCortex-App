"""
CivilCortex - Deterministic Demo Engine
Provides centralized scenario lookup and state injection for all pipeline agents.
"""

from typing import Dict, Any, List
from demo.scenarios import DEMO_SCENARIOS, DEFAULT_SCENARIO_ID

def get_demo_scenario(scenario_id: str = None) -> Dict[str, Any]:
    """
    Returns the exact deterministic scenario data for the requested scenario_id.
    Falls back to 'hairline_crack' if scenario_id is unrecognized or None.
    """
    if not scenario_id or scenario_id not in DEMO_SCENARIOS:
        scenario_id = DEFAULT_SCENARIO_ID
    return DEMO_SCENARIOS[scenario_id]

def list_demo_scenarios() -> List[Dict[str, str]]:
    """
    Returns list of available demo scenarios for API/frontend dropdowns.
    """
    return [
        {"id": s_id, "title": data["title"], "crack_detected": data["crack_detected"]}
        for s_id, data in DEMO_SCENARIOS.items()
    ]

def get_demo_condition_state(scenario_id: str = None) -> Dict[str, Any]:
    """
    Returns the Agent 1 condition output dictionary for Demo Mode.
    """
    scenario = get_demo_scenario(scenario_id)
    return {
        "scenario_id": scenario["scenario_id"],
        "crack_detected": scenario["crack_detected"],
        "crack_probability": scenario["crack_probability"],
        "crack_type": scenario["crack_type"],
        "severity": scenario["severity"],
        "health_score": scenario["health_score"],
        "condition": scenario["condition"],
        "mode": "demo"
    }

def get_demo_report_text(scenario_id: str = None, structure_type: str = "tunnel") -> str:
    """
    Generates a deterministic, beautifully formatted Markdown inspection report.
    """
    sc = get_demo_scenario(scenario_id)
    
    detection_badge = "CRACK DETECTED" if sc["crack_detected"] else "NO CRACK DETECTED"
    
    materials_list = "\n".join([f"- {m}" for m in sc["required_materials"]])
    
    report = f"""### CivilCortex Structural Health Assessment Report

> **Demonstration Mode Notice:** This assessment was evaluated in **Controlled Prototype / Demo Mode** for testing and demonstration purposes.

---

### 1. Condition & Detection Summary
* **Detection Status:** **{detection_badge}**
* **Defect Classification:** **{sc['crack_type']}**
* **Visual Severity:** **{sc['severity'].upper()}**
* **Crack Probability:** **{sc['crack_probability']*100:.1f}%**
* **Structural Health Score:** **{sc['health_score']} / 100**
* **Structural Condition:** **{sc['condition']}**

---

### 2. Risk & Priority Assessment
* **Assessed Risk Score:** **{sc['risk_score']} / 100**
* **Overall Risk Level:** **{sc['risk_level']}**
* **Target Structure:** **{structure_type.capitalize()}**
* **Intervention Priority:** **{sc['priority']}**
* **Turnaround Time:** Within **{sc['days']} day(s)**

---

### 3. Recommended Remediation Strategy
* **Action Required:** {sc['recommended_action']}
* **Repair Method:** {sc['repair_method']}
* **Required Workforce:** **{sc['required_workers']} technician(s) / engineer(s)**
* **Estimated Cost (INR):** **{sc['estimated_cost']}**

#### Required Materials & Equipment:
{materials_list}

---

### 4. Regulatory Compliance & Applicable Standards
{sc['rag_context']}

---
*Report generated deterministically by CivilCortex LangGraph Multi-Agent Architecture.*
"""
    return report.strip()
