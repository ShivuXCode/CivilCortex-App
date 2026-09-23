from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.domain_models import Material, LaborRate

class CostEngine:
    @staticmethod
    def estimate_repair(
        db: Session, 
        repair_method_name: str, 
        estimated_material_quantity: float, 
        material_name: str,
        labor_category: str,
        estimated_labor_days: float
    ) -> Dict[str, Any]:
        """
        Calculates a deterministic cost based on the database rates.
        """
        # Fetch rates from DB
        material = db.query(Material).filter(Material.name.ilike(f"%{material_name}%")).first()
        labor = db.query(LaborRate).filter(LaborRate.category.ilike(f"%{labor_category}%")).first()

        if not material or not labor:
            return {
                "method_name": repair_method_name,
                "currency": "INR",
                "status": "DATA_UNAVAILABLE",
                "message": "Real pricing data is required. Missing material or labor rates in the database.",
                "material_cost": None,
                "labor_cost": None,
                "total_range_low": "N/A",
                "total_range_high": "N/A",
                "details_json": {
                    "material_requested": material_name,
                    "labor_requested": labor_category,
                    "overhead_contingency_assumption": "20%"
                }
            }

        mat_rate = material.unit_rate
        lab_rate = labor.daily_rate

        base_material_cost = estimated_material_quantity * mat_rate
        base_labor_cost = estimated_labor_days * lab_rate

        # Add overhead and contingency (e.g. 20%)
        overhead_multiplier = 1.2
        total = (base_material_cost + base_labor_cost) * overhead_multiplier

        # Provide a ±15% range for estimation
        range_low = total * 0.85
        range_high = total * 1.15

        return {
            "method_name": repair_method_name,
            "currency": "INR",
            "material_cost": round(base_material_cost, 2),
            "labor_cost": round(base_labor_cost, 2),
            "total_range_low": round(range_low, 2),
            "total_range_high": round(range_high, 2),
            "details_json": {
                "material_used": material.name if material else material_name,
                "material_rate": mat_rate,
                "labor_category": labor.category if labor else labor_category,
                "labor_rate": lab_rate,
                "overhead_contingency": "20%"
            }
        }
