import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from pydantic import BaseModel, Field
from core.logger import logger

from core.config import settings
from demo.demo_engine import get_demo_scenario

class MaintenanceActionResponse(BaseModel):
    maintenance_action: str = Field(description="The specific engineering action required, e.g., 'Concrete Reinforcement'")
    source_document: str = Field(description="The exact name of the source document and section referenced from the context.")

def plan_maintenance(state: dict) -> dict:
    # 0. Controlled Prototype / Demo Mode Execution
    if getattr(settings, "DEMO_MODE", False):
        scenario_id = state.get("scenario") or getattr(settings, "DEFAULT_DEMO_SCENARIO", "hairline_crack")
        sc = get_demo_scenario(scenario_id)
        return {
            "maintenance_action": sc["recommended_action"],
            "rag_context": sc["rag_context"]
        }

    priority = state.get("priority", "Routine")
    crack_type = state.get("crack_type", "")
    
    if crack_type.lower() == "none" or crack_type == "Unknown":
        return {
            "maintenance_action": "No maintenance required.",
            "rag_context": "N/A"
        }
    
    # 1. Retrieve RAG Context
    rag_context = ""
    docs_found = False
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "chroma_db")
    
    if os.path.exists(db_path):
        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
            db = Chroma(persist_directory=db_path, embedding_function=embeddings)
            
            # Query the database with metadata filtering
            docs = db.similarity_search(crack_type, k=2, filter={"category": "structural_standard"})
            if docs:
                rag_context = "\n\n".join([f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}" for doc in docs])
                # Check if it's genuinely populated
                if len(rag_context.strip()) > 10:
                    docs_found = True
        except Exception as e:
            logger.error(f"RAG Retrieval Error: {e}")
            pass
            
    # 2. Prevent Hallucination: If no regulatory context is found, do NOT let the LLM guess.
    if not docs_found:
        return {
            "maintenance_action": "Manual Engineer Review Required - No standard found",
            "rag_context": "No specific regulatory guidelines found in knowledge base."
        }
        
    # 3. Use LLM to determine the best action, strictly grounded in the retrieved RAG Context
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.1)
        structured_llm = llm.with_structured_output(MaintenanceActionResponse)
        
        prompt = f"""
        Based strictly on the following regulatory tunnel and concrete standards:
        {rag_context}
        
        Given a {crack_type} crack with {priority} priority, what is the single best engineering maintenance action to perform according to the standard? Respond concisely. Do not invent any actions outside of the provided text.
        Also provide the exact name of the source document referenced.
        """
        
        response = structured_llm.invoke(prompt)
        maintenance_action = f"{response.maintenance_action} (Source: {response.source_document})"
    except Exception as e:
        logger.error(f"LLM Error during planning: {e}")
        maintenance_action = "Manual Engineer Review Required - LLM Error"
    
    return {
        "maintenance_action": maintenance_action,
        "rag_context": rag_context
    }
