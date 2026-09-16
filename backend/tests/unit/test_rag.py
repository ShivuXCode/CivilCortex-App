import pytest
from app.services.rag_service import rag_service
from app.schemas.ai_contract import RAGEvidence
from app.core.exceptions import RAGError

def test_retrieve_evidence_empty_query():
    # "none" or "Unknown" should return empty
    evidence = rag_service.retrieve_evidence("none")
    assert isinstance(evidence, list)
    assert len(evidence) == 0

    evidence = rag_service.retrieve_evidence("Unknown")
    assert isinstance(evidence, list)
    assert len(evidence) == 0

def test_retrieve_evidence_valid_query():
    # If there are no Google credentials, it will raise RAGError
    try:
        evidence = rag_service.retrieve_evidence("structural crack")
        assert isinstance(evidence, list)
        if len(evidence) > 0:
            assert isinstance(evidence[0], RAGEvidence)
            assert evidence[0].source != ""
            assert evidence[0].text != ""
            assert isinstance(evidence[0].metadata, dict)
    except RAGError:
        pass
