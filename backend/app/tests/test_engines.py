import pytest
import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.risk_engine import RiskEngine
from app.services.priority_engine import PriorityEngine
from app.services.cost_engine import CostEngine
from app.schemas.api_models import CVDetection, CVGeometry, CVMeasurement

def test_risk_engine():
    """
    Test that RiskEngine correctly applies the Structure Type Multiplier
    and contextualizes morphology based on element criticality and severity.
    """
    # 1. Test a low-risk scenario
    cv_result_low = CVDetection(
        detection_id="mock-id-1",
        defect_type="hairline",
        morphology_tags=["diagonal"],
        model_confidence=0.9,
        bounding_box=[0, 0, 10, 10]
    )
    result1 = RiskEngine.calculate_risk(element_type="partition wall", cv_result=cv_result_low, severity_level="low")
    
    # Base = 20.0 (low). Multiplier = 0.8 (partition wall). 
    # Diagonal morphology on non-critical element = 1.05 mult
    # Raw score = 20 * 0.8 * 1.05 = 16.8
    assert result1["score"] == 16.8
    assert result1["level"] == "Low"

    # 2. Test a high-risk scenario
    cv_result_high = CVDetection(
        detection_id="mock-id-2",
        defect_type="crack",
        morphology_tags=["diagonal"],
        model_confidence=0.9,
        bounding_box=[0, 0, 10, 10]
    )
    result2 = RiskEngine.calculate_risk(element_type="column", cv_result=cv_result_high, severity_level="critical")
    # Base = 80.0 (critical). Multiplier = 1.5 (column > 1.2). 
    # Diagonal morphology on critical element + critical severity (>=40) = 1.25 mult
    # Raw = 80.0 * 1.5 * 1.25 = 150.0. Max is 100.
    assert result2["score"] == 100.0
    assert result2["level"] == "High"

def test_priority_engine():
    """
    Test that priority engine correctly enforces Immediate on high risk or critical severity.
    """
    res = PriorityEngine.calculate_priority(risk_level="High", severity_level="Medium")
    assert res["level"] == "Immediate"
    assert res["max_days"] == 7

    res2 = PriorityEngine.calculate_priority(risk_level="Medium", severity_level="High")
    assert res2["level"] == "Urgent"
    assert res2["max_days"] == 30

def test_cost_engine():
    """
    Test that the cost engine performs the math correctly given dummy values.
    """
    from unittest.mock import MagicMock
    db = MagicMock()
    # Mocking the DB query to return None so it hits the default 100 and 500
    db.query().filter().first.return_value = None
    
    res = CostEngine.estimate_repair(db, "Epoxy Injection", 2.0, "Epoxy", "Mason", 1.0)
    # Material: 2.0 * 100 = 200
    # Labor: 1.0 * 500 = 500
    # Base Total = 700. Overhead = 700 * 1.2 = 840
    # Range = 840 * 0.85 = 714, 840 * 1.15 = 966
    
    assert res["material_cost"] == 200.0
    assert res["labor_cost"] == 500.0
    assert res["total_range_low"] == 714.0
    assert res["total_range_high"] == 966.0

