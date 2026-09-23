from typing import Optional, Dict, Any
from app.schemas.api_models import CVDetection

class RiskEngine:
    @staticmethod
    def calculate_risk(
        element_type: str, 
        cv_result: Optional[CVDetection], 
        severity_level: str
    ) -> Dict[str, Any]:
        """
        Calculate a deterministic risk score based on the structural element
        and the observed severity. Morphology is only one of many inputs.
        """
        # Base score from observed severity (human/overall assessment)
        severity_scores = {
            "low": 20.0,
            "medium": 40.0,
            "high": 60.0,
            "critical": 80.0
        }
        
        normalized_severity = severity_level.lower()
        if normalized_severity not in severity_scores:
            raise ValueError(f"Invalid severity level: '{severity_level}'. Must be one of: low, medium, high, critical.")
            
        base_score = severity_scores[normalized_severity]

        # Element criticality multiplier
        element_multipliers = {
            "column": 1.5,
            "beam": 1.4,
            "load-bearing wall": 1.3,
            "foundation": 1.5,
            "partition wall": 0.8,
            "slab": 1.1
        }
        elem_mult = element_multipliers.get(element_type.lower(), 1.0)

        # Morphology alone is NOT a failure mechanism. 
        # A diagonal crack on a non-load-bearing wall is low risk. 
        # A diagonal crack on a column with high severity is high risk.
        morphology_mult = 1.0
        if cv_result:
            tags = [t.lower() for t in cv_result.morphology_tags]
            # Only apply morphology multiplier if element is critical AND severity is at least medium
            if ("diagonal" in tags or "branching" in tags):
                if elem_mult > 1.2 and base_score >= 40.0:
                    morphology_mult = 1.25 # Contextualized risk
                else:
                    morphology_mult = 1.05 # Minor visual evidence on non-critical element

            if cv_result.defect_type.lower() == "spalling" or "exposed rebar" in tags:
                if elem_mult > 1.2:
                    morphology_mult = max(morphology_mult, 1.3)
                else:
                    morphology_mult = max(morphology_mult, 1.1)

        # Calculate final raw score
        raw_score = base_score * elem_mult * morphology_mult
        final_score = min(100.0, max(0.0, raw_score))

        # Determine level
        if final_score >= 75:
            level = "High"
        elif final_score >= 40:
            level = "Medium"
        else:
            level = "Low"

        return {
            "score": round(final_score, 2),
            "level": level,
            "factors_json": {
                "base_severity_score": base_score,
                "element_multiplier": elem_mult,
                "morphology_multiplier": morphology_mult
            }
        }
