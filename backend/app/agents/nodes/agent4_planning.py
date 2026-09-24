from app.agents.state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.logger import logger

def plan_maintenance(state: AgentState) -> dict:
    rag_evidence = state.get('rag_evidence')
    severity = state.get('severity')
    crack_type = state.get('crack_type')
    
    # 1. Validate inputs before doing any LLM or RAG work
    valid_severities = ["low", "medium", "high", "critical", "none"]
    if not severity or severity.lower() not in valid_severities:
        logger.warning(f"Agent 4: Invalid or unknown severity ({severity}). Halting repair planning.")
        return {
            "maintenance_action": f"REQUIRES_REVIEW: Cannot determine engineering recommendation due to unknown or missing condition severity.",
            "required_workers": None,
            "required_materials": []
        }
        
    if not crack_type or crack_type.lower() in ["unknown", "none"]:
        logger.warning(f"Agent 4: Invalid or unknown crack type ({crack_type}). Halting repair planning.")
        return {
            "maintenance_action": "REQUIRES_REVIEW: Insufficient defect type evidence to propose repair considerations.",
            "required_workers": None,
            "required_materials": []
        }
    
    if not rag_evidence or len(rag_evidence) == 0:
        logger.warning("Agent 4: No RAG evidence available. Halting repair planning.")
        return {
            "maintenance_action": "REQUIRES_REVIEW: Insufficient standard evidence to propose repair materials.",
            "required_workers": None,
            "required_materials": []
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
Based ONLY on the retrieved engineering standards, provide a short "RAG-supported repair consideration" summary.

Defect Details:
- Type: {state.get('crack_type')}
- Severity: {state.get('severity')}
- Structure: {state.get('structure_type')}

Retrieved Engineering Standards:
{context_str}

Instructions:
1. Synthesize a 2-3 sentence repair consideration based purely on the standards.
2. DO NOT invent repair methods, material quantities, or worker counts.
3. Your output should read like a set of engineering considerations for a human reviewer.
"""
        response = llm.invoke(prompt)
        content_str = response.content
        if isinstance(content_str, list):
            content_str = str(content_str[0].get("text", content_str))
        
        action = "RAG-Supported Repair Considerations: " + str(content_str).strip()
        
    except Exception as e:
        logger.error(f"Agent 4: LLM invocation failed: {e}")
        action = f"REQUIRES_REVIEW: LLM processing failed ({str(e)})."

    return {
        "maintenance_action": action,
        "required_workers": None,
        "required_materials": []
    }
