from app.agents.state import AgentState
from app.services.cost_engine import CostEngine
from app.db.session import SessionLocal
import json

def optimize_resources(state: AgentState) -> dict:
    repair_method = state.get("maintenance_action", "Unknown Repair")
    workers = state.get("required_workers", 1)
    materials = state.get("required_materials", [])
    
    primary_material = materials[0] if materials else "Concrete"
    labor_category = "General Labor"
    if "high" in state.get("severity", "low").lower() or "critical" in state.get("severity", "low").lower():
        labor_category = "Specialist Structural"

    estimated_labor_days = float(workers * 2.0)
    estimated_material_qty = 10.0

    with SessionLocal() as db:
        cost_data = CostEngine.estimate_repair(
            db=db,
            repair_method_name=repair_method,
            estimated_material_quantity=estimated_material_qty,
            material_name=primary_material,
            labor_category=labor_category,
            estimated_labor_days=estimated_labor_days
        )

    if cost_data.get("status") == "DATA_UNAVAILABLE":
        estimated_cost_str = "DATA_UNAVAILABLE - Requires manual cost estimation"
    else:
        estimated_cost_str = f"{cost_data.get('currency', 'INR')} {cost_data.get('total_range_low', 'N/A')} - {cost_data.get('total_range_high', 'N/A')}"

    return {
        "estimated_cost": estimated_cost_str
    }
