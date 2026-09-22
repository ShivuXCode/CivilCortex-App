import pytest
from unittest.mock import patch, MagicMock
from app.agents.nodes.agent6_llm import generate_recommendation
import json

@patch("app.agents.nodes.agent6_llm.ChatGoogleGenerativeAI")
def test_agent6_missing_api_key(mock_llm):
    # Simulate missing credentials exception
    mock_llm.side_effect = Exception("Default credentials were not found")
    
    state = {
        "crack_type": "hairline_crack",
        "health_score": 80,
        "risk_level": "Low",
        "priority": "Routine",
        "maintenance_action": "Monitor crack width",
        "rag_context": "Test source\nCrack standard"
    }
    
    result = generate_recommendation(state)
    assert "recommendation" in result
    assert "This report is automatically generated using heuristic structural mappings" in result["recommendation"]

@patch("app.agents.nodes.agent6_llm.ChatGoogleGenerativeAI")
def test_agent6_no_maintenance_required(mock_llm):
    state = {
        "crack_type": "none",
        "maintenance_action": "No maintenance required."
    }
    
    result = generate_recommendation(state)
    assert "recommendation" in result
    assert "No maintenance action is required" in result["recommendation"]
    
    # LLM should not be called
    mock_llm.assert_not_called()

@patch("app.agents.nodes.agent6_llm.ChatGoogleGenerativeAI")
def test_agent6_manual_review_required(mock_llm):
    state = {
        "crack_type": "severe_crack",
        "maintenance_action": "Manual Engineer Review Required - No standard found"
    }
    
    result = generate_recommendation(state)
    assert "recommendation" in result
    
    # It returns a JSON string, let's parse it
    parsed = json.loads(result["recommendation"])
    assert parsed["status"] == "MANUAL_REVIEW"
    assert parsed["reason"] == "NO_STANDARD_FOUND"
    
    # LLM should not be called
    mock_llm.assert_not_called()

@patch("app.agents.nodes.agent6_llm.ChatGoogleGenerativeAI")
def test_agent6_valid_generation(mock_llm):
    # Mock LLM successful invocation
    mock_llm_instance = MagicMock()
    mock_llm.return_value = mock_llm_instance
    mock_structured = MagicMock()
    mock_llm_instance.with_structured_output.return_value = mock_structured
    
    # Mock structured response
    class MockResponse:
        recommendation = "### Condition Summary\nValid mock report generated."
        
    mock_structured.invoke.return_value = MockResponse()
    
    state = {
        "crack_type": "hairline_crack",
        "health_score": 80,
        "risk_level": "Low",
        "priority": "Routine",
        "maintenance_action": "Monitor crack width",
        "rag_context": "Test source\nCrack standard"
    }
    
    result = generate_recommendation(state)
    assert "recommendation" in result
    assert "Valid mock report generated." in result["recommendation"]
    
    # Verify LLM was called
    mock_structured.invoke.assert_called_once()
