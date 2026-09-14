from typing import Dict, Any

class PriorityEngine:
    @staticmethod
    def calculate_priority(risk_level: str, severity_level: str) -> Dict[str, Any]:
        """
        Deterministically calculate priority and max days to repair based on Risk and Severity.
        """
        rl = risk_level.lower()
        sl = severity_level.lower()

        if rl == "high" or sl == "critical":
            level = "Immediate"
            max_days = 7
        elif rl == "medium" and sl == "high":
            level = "Urgent"
            max_days = 30
        elif rl == "medium":
            level = "High Priority"
            max_days = 90
        else:
            level = "Routine"
            max_days = 365

        return {
            "level": level,
            "max_days": max_days,
            "factors_json": {
                "risk_level_input": risk_level,
                "severity_level_input": severity_level
            }
        }
