from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import time
from core.logger import logger

from core.config import settings
from demo.demo_engine import get_demo_report_text

class RecommendationResponse(BaseModel):
    recommendation: str = Field(description="A comprehensive, multi-paragraph recommendation report for stakeholders")

def generate_recommendation(state: dict) -> dict:
    # 0. Controlled Prototype / Demo Mode Execution
    if getattr(settings, "DEMO_MODE", False):
        scenario_id = state.get("scenario") or getattr(settings, "DEFAULT_DEMO_SCENARIO", "hairline_crack")
        structure_type = state.get("structure_type", "tunnel")
        report_text = get_demo_report_text(scenario_id, structure_type=structure_type)
        return {
            "recommendation": report_text
        }

    # Gather state
    crack_type = state.get("crack_type", "Unknown")
    health_score = state.get("health_score", 100)
    risk_level = state.get("risk_level", "Low")
    priority = state.get("priority", "Routine")
    action = state.get("maintenance_action", "None")
    cost = state.get("estimated_cost", "$0")
    workers = state.get("required_workers", 0)
    materials = state.get("required_materials", [])
    rag_context = state.get("rag_context", "None provided.")
    
    # Check for API rate limits and connection errors first
    if "API_ERROR_RATE_LIMIT" in crack_type:
        import json
        return {
            "recommendation": json.dumps({
                "status": "RATE_LIMITED",
                "reason": "API_ERROR_RATE_LIMIT",
                "details": "The Google Gemini API free-tier quota (20 requests per minute) has been reached due to rapid testing. Please wait approximately 30-60 seconds before submitting another image to allow the quota bucket to refill."
            })
        }
        
    if "API_ERROR" in crack_type:
        return {
            "recommendation": "**System Error: AI Engine Unreachable**\n\nThe AI classification engine encountered an unknown error. Please try again."
        }
        
    # Check if manual review was required due to empty RAG state
    if "Manual Engineer Review Required" in action:
        import json
        return {
            "recommendation": json.dumps({
                "status": "MANUAL_REVIEW",
                "reason": "NO_STANDARD_FOUND",
                "details": f"AUTOMATED PIPELINE HALTED.\n\nReason: {action}\n\nNo standard was found in the knowledge base. To prevent hallucination, the LLM has been bypassed. A human engineer must review this defect."
            })
        }
        
    if "No maintenance required" in action or crack_type.lower() == "none" or crack_type == "Unknown":
        return {
            "recommendation": "### Condition Summary\n\n**Status:** Excellent\n\nNo structural defects or cracks were detected in the provided image. The surface appears to be clean and undamaged.\n\nNo maintenance action is required at this time."
        }
    
    prompt = f"""
    Act as a Lead Civil Engineer and Standards Compliance Officer. 
    Write a comprehensive, highly readable recommendation report for stakeholders based on the following automated analysis:
    
    - Crack Type: {crack_type}
    - Health Score (0-100): {health_score}
    - Overall Risk Level: {risk_level}
    - Priority: {priority}
    - Proposed Action: {action}
    - Estimated Cost: {cost}
    - Required Workers: {workers}
    - Materials: {', '.join(materials)}
    
    CRITICAL INSTRUCTION: You must format your response beautifully using Markdown. Make it extremely eye-pleasing and easy to read. 
    Use bold headers (e.g. ### Condition Summary), bullet points for all lists (like materials or action steps), and bold text for key metrics. Do not output massive walls of text.
    
    You must base your recommendation strictly on the following Regulatory Standards. 
    You MUST explicitly cite the specific clauses from these standards in your report to justify the action and materials. Do NOT invent or hallucinate any standards outside of this text:
    
    REGULATORY STANDARDS RETRIEVED (RAG Context):
    {rag_context}
    """
    
    # Fault Tolerance: Retry logic for API calls
    max_retries = 3
    for attempt in range(max_retries):
        try:
            llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.2)
            structured_llm = llm.with_structured_output(RecommendationResponse)
            
            response = structured_llm.invoke(prompt)
            return {
                "recommendation": response.recommendation
            }
        except Exception as e:
            logger.error(f"LLM API Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait 2 seconds before retrying
            else:
                return {
                    "recommendation": "Error: Unable to generate report due to API timeout after multiple attempts. Please check network connection or API limits."
                }

