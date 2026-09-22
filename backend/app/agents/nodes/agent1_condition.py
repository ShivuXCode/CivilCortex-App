import os
import io
import base64
import numpy as np
from pydantic import BaseModel, Field
from app.core.logger import logger

class VisionClassificationResponse(BaseModel):
    crack_type: str = Field(description="The specific type of structural defect identified, e.g. 'Deep Foundation Settlement', 'Spalling', 'Hairline Crack'. If no crack, return 'None'.")
    severity: str = Field(description="The severity level of the defect: 'low', 'medium', or 'high'. If no crack, return 'low'.")

def assess_condition(state: dict) -> dict:
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
            
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.0)
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
            logger.warning(f"Gemini classification unavailable/failed ({e}). Falling back to local offline heuristics.")
            if health_score >= 95:
                crack_type = "None"
                severity = "low"
            elif largest_component_area > 1000 and mask_coverage > 0.05:
                crack_type = "Spalling"
                severity = "high"
            elif component_count > 5:
                crack_type = "Network/Alligator Cracking"
                severity = "medium"
            else:
                crack_type = "Hairline Crack"
                severity = "low" if health_score >= 80 else "medium"
            
    return {
        "health_score": health_score,
        "condition": condition,
        "crack_type": crack_type,
        "severity": severity
    }
