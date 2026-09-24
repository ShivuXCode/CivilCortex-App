from app.agents.state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.logger import logger

def generate_recommendation(state: AgentState) -> dict:
    structure_type = state.get('structure_type', 'unknown structure')
    severity = state.get('severity', 'low')
    crack_type = state.get('crack_type', 'crack')
    risk_level = state.get('risk_level', 'unknown')
    priority = state.get('priority', 'unknown')
    maintenance_action = state.get('maintenance_action', 'unknown')
    days = state.get('days', 'unknown')
    
    rag_evidence = state.get('rag_evidence')
    
    if not rag_evidence or len(rag_evidence) == 0:
        logger.warning("Agent 6: No RAG evidence provided. Halting recommendation synthesis.")
        return {
            "rag_context": "INSUFFICIENT_EVIDENCE",
            "recommendation": "REQUIRES_REVIEW: The AI cannot generate an engineering recommendation because no valid engineering standards were retrieved from the database."
        }
        
    context_str = ""
    for ev in rag_evidence:
        source = ev.get('source', 'Unknown Source')
        text = ev.get('text', '')
        context_str += f"Source: {source}\n{text}\n\n"
        
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.1)
        
        prompt = f"""
Act as a Civil Engineering Assistant.
Synthesize a repair recommendation for a structural defect based ONLY on the provided engineering standards.

Defect Details:
- Type: {crack_type}
- Structure: {structure_type}
- Assessed Severity: {severity}
- Risk Level: {risk_level}
- Priority: {priority}
- Proposed Action: {maintenance_action} (within {days} days)

Retrieved Engineering Standards:
{context_str}

Instructions:
1. Explain how the retrieved standards apply to the defect.
2. Formulate a final recommendation.
3. Clearly distinguish the RAG-supported evidence from your own AI synthesis (e.g., use headers or explicitly state "According to the retrieved standards...").
4. DO NOT invent citations, measurements, or engineering facts that are not explicitly present in the retrieved standards.
"""
        response = llm.invoke(prompt)
        recommendation = response.content
        if isinstance(recommendation, list):
            recommendation = str(recommendation[0].get("text", recommendation))
        
    except Exception as e:
        logger.error(f"Agent 6: LLM invocation failed: {e}")
        return {
            "rag_context": "INSUFFICIENT_EVIDENCE",
            "recommendation": f"REQUIRES_REVIEW: LLM processing failed ({str(e)})."
        }
        
    return {
        "rag_context": context_str.strip(),
        "recommendation": recommendation
    }
