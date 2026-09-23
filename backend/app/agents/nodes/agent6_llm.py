from app.agents.state import AgentState
from app.services.rag_service import rag_service

def generate_recommendation(state: AgentState) -> dict:
    # Fetch RAG context based on crack type and severity
    structure_type = state.get('structure_type', 'unknown structure')
    severity = state.get('severity', 'low')
    crack_type = state.get('crack_type', 'crack')
    query = f"Standards for repairing {severity} {crack_type} cracks in {structure_type}"
    
    try:
        results = rag_service.query(query, n_results=3)
        context = "\n".join([doc for doc in results["documents"][0]]) if results and results["documents"] else "No specific standards found."
    except Exception:
        context = "No specific standards found."
        
    recommendation = f"Based on the {severity} severity {crack_type} crack in the {structure_type}, "
    recommendation += f"the risk level is {state.get('risk_level', 'unknown')} with priority {state.get('priority', 'unknown')}. "
    recommendation += f"Action required: {state.get('maintenance_action', 'unknown')} within {state.get('days', 'unknown')} days."
    
    return {
        "rag_context": context,
        "recommendation": recommendation
    }
