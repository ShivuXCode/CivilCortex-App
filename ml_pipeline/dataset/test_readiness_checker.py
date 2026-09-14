import pytest
from pathlib import Path
import json
from readiness_checker import FieldDataReadinessChecker
import tempfile
import os

@pytest.fixture
def temp_workspace():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)

def test_approved_configuration_no_ambiguity(temp_workspace):
    targets = {
        "target_resolution": {
            "status": "APPROVED",
            "approved_option": "option_b_3100_total",
            "options": {
                "option_b_3100_total": {
                    "minimum_defect_instances": 3100,
                    "defect_type_distribution": {
                        "crack": {"minimum_instances": 1500},
                        "spalling": {"minimum_instances": 800},
                        "efflorescence": {"minimum_instances": 800}
                    }
                }
            }
        },
        "acceptance_gate": {
            "minimum_distinct_sites": 10
        },
        "hard_negative_target": {
            "minimum_instances": 800
        }
    }
    target_path = temp_workspace / "targets.json"
    target_path.write_text(json.dumps(targets))
    
    checker = FieldDataReadinessChecker(target_path)
    metadata_dir = temp_workspace / "metadata"
    metadata_dir.mkdir()
    res = checker.check_readiness(metadata_dir)
    # The resolution is APPROVED, but the actual data count is 0.
    # Therefore, the readiness status must be BLOCKED, not PASS.
    assert res["status"] == "BLOCKED"
    assert any("need 3100" in b for b in res["blockers"])
    assert any("need 10" in b for b in res["blockers"])

def test_mathematically_inconsistent(temp_workspace):
    targets = {
        "target_resolution": {
            "status": "APPROVED",
            "approved_option": "option",
            "options": {
                "option": {
                    "minimum_defect_instances": 2000,
                    "defect_type_distribution": {
                        "crack": {"minimum_instances": 1500},
                        "spalling": {"minimum_instances": 800},
                        "efflorescence": {"minimum_instances": 800}
                    }
                }
            }
        }
    }
    target_path = temp_workspace / "targets.json"
    target_path.write_text(json.dumps(targets))
    with pytest.raises(ValueError, match="Mathematically inconsistent targets: class minimums \\(3100\\) exceed total minimum \\(2000\\)"):
        FieldDataReadinessChecker(target_path)

def test_mathematically_consistent(temp_workspace):
    targets = {
        "target_resolution": {
            "status": "APPROVED",
            "approved_option": "option",
            "options": {
                "option": {
                    "minimum_defect_instances": 3100,
                    "defect_type_distribution": {
                        "crack": {"minimum_instances": 1500},
                        "spalling": {"minimum_instances": 800},
                        "efflorescence": {"minimum_instances": 800}
                    }
                }
            }
        },
        "hard_negative_target": {
            "minimum_instances": 800
        }
    }
    target_path = temp_workspace / "targets.json"
    target_path.write_text(json.dumps(targets))
    checker = FieldDataReadinessChecker(target_path)  # Should not raise
    assert checker is not None

def test_hard_negatives_excluded_from_physical_defects(temp_workspace):
    targets = {
        "target_resolution": {
            "status": "APPROVED",
            "approved_option": "option",
            "options": {
                "option": {
                    "minimum_defect_instances": 1,
                    "defect_type_distribution": {
                        "crack": {"minimum_instances": 1},
                        "spalling": {"minimum_instances": 0},
                        "efflorescence": {"minimum_instances": 0}
                    }
                }
            }
        },
        "acceptance_gate": {
            "minimum_distinct_sites": 1
        },
        "hard_negative_target": {
            "minimum_instances": 1
        }
    }
    target_path = temp_workspace / "targets.json"
    target_path.write_text(json.dumps(targets))
    checker = FieldDataReadinessChecker(target_path)
    
    metadata_dir = temp_workspace / "metadata"
    metadata_dir.mkdir()
    
    rec = {
        "site_id": "site_1",
        "defects": [
            {"defect_instance_id": "hn1", "defect_type": "hard_negative"}
        ]
    }
    (metadata_dir / "1.json").write_text(json.dumps(rec))
    
    res = checker.check_readiness(metadata_dir)
    # The hard negative should NOT increase physical defect count or crack count
    assert res["hard_negatives"] == 1
    assert res["crack_instances"] == 0
    assert any("Insufficient crack instances" in b for b in res["blockers"])
    assert any("Insufficient defect instances. Found 1, need 1" not in b for b in res["blockers"])
