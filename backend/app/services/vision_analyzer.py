import base64
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class VisionResult(BaseModel):
    crack_type: str = Field(description="The specific type of structural defect identified, e.g. 'Deep Foundation Settlement', 'Spalling', 'Hairline Crack'")
    severity: str = Field(description="The severity level of the defect: 'low', 'medium', or 'high'")

def analyze_defect_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> VisionResult:
    """
    Analyzes an image of a structural defect and extracts its type and severity.
    """
    # Initialize the multimodal model
    llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.1)
    structured_llm = llm.with_structured_output(VisionResult)
    
    # Encode the image
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    
    prompt = "Analyze this image of a structural defect. Identify the crack type (e.g., 'Deep Foundation Settlement', 'Spalling', 'Hairline Crack') and classify its severity strictly as 'low', 'medium', or 'high'."
    
    # Create the multimodal message
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{encoded_image}"
                }
            }
        ]
    )
    
    # Invoke the model
    response = structured_llm.invoke([message])
    return response
