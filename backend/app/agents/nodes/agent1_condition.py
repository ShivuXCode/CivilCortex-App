import os
import io
import base64
import numpy as np
from pydantic import BaseModel, Field
from app.core.logger import logger

from app.core.config import settings
from app.demo.demo_engine import get_demo_condition_state


class VisionClassificationResponse(BaseModel):
    crack_type: str = Field(description="The specific type of structural defect identified, e.g. 'Deep Foundation Settlement', 'Spalling', 'Hairline Crack'. If no crack, return 'None'.")
    severity: str = Field(description="The severity level of the defect: 'low', 'medium', or 'high'. If no crack, return 'low'.")

def assess_condition(state: dict) -> dict:
    # 0. Controlled Prototype / Demo Mode Execution
    if getattr(settings, "DEMO_MODE", False):
        scenario_id = state.get("scenario") or getattr(settings, "DEFAULT_DEMO_SCENARIO", "hairline_crack")
        demo_state = get_demo_condition_state(scenario_id)
        logger.info(f"[DEMO MODE] Executed scenario '{demo_state['scenario_id']}': {demo_state['crack_type']} (Health: {demo_state['health_score']})")
        return demo_state

    # Real ML Pipeline Execution (Preserved)
    image_bytes = state.get("image_bytes")
    
    health_score = 100
    condition = "Excellent"
    crack_type = "Unknown"
    severity = "low"
    
    if image_bytes:
        # 1. Extract CV geometric metrics from the state
        mask_coverage = state.get("mask_coverage", 0.0) or 0.0
        component_count = state.get("component_count", 0) or 0
        largest_component_area = state.get("largest_component_area", 0) or 0
        
        penalty = int(mask_coverage * 500)
        health_score = max(0, 100 - penalty)
        condition = "Critical" if health_score < 60 else ("Fair" if health_score < 90 else "Excellent")
        logger.info(f"Using CV geometric metrics. Mask coverage: {mask_coverage:.4f}, Components: {component_count}, Largest Area: {largest_component_area}, Health Score: {health_score}")

        # 2. Use Gemini Vision to classify the defect type based on the Keras findings
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage
            
            llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.0)
            structured_llm = llm.with_structured_output(VisionClassificationResponse)
            
            img_b64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Inform Gemini of the local AI's findings
            if health_score >= 95:
                prompt = "Analyze this image of a concrete surface. The local segmentation model detected NO significant cracks (Health Score is near perfect). Confirm there is no crack by returning crack_type 'None' and severity 'low'."
            else:
                prompt = f"Analyze this image of a structural defect. The local AI detected a crack covering {mask_coverage*100:.1f}% of the area, consisting of {component_count} connected components, with the largest component area being {largest_component_area} pixels. Identify the crack type (e.g., 'Spalling', 'Hairline Crack') and classify its visual severity as 'low', 'medium', or 'high'."
            
            msg = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            )
            
            gemini_check = structured_llm.invoke([msg])
            crack_type = gemini_check.crack_type
            severity = gemini_check.severity.lower()
            logger.info(f"Gemini Vision Classification: {crack_type} | Severity: {severity}")
            
        except Exception as e:
            logger.error(f"Gemini classification failed... {e}")
            if "429" in str(e) or "quota" in str(e).lower() or "exhausted" in str(e).lower():
                crack_type = "API_ERROR_RATE_LIMIT"
            else:
                crack_type = "API_ERROR_UNKNOWN"
            
    return {
        "health_score": health_score,
        "condition": condition,
        "crack_type": crack_type,
        "severity": severity
    }
