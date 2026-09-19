from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class RAGEvidence(BaseModel):
    source: str
    text: str
    metadata: Dict[str, Any]
    relevance_score: Optional[float] = None

# --- AI Input Contract ---

class CVModelMetadata(BaseModel):
    model_name: str
    model_version: str
    model_status: str

class CVOutputContext(BaseModel):
    defect_type: str = Field(description="The type of defect detected by the CV model, e.g., 'crack'")
    confidence: float = Field(description="The model's confidence score [0.0 - 1.0]")
    mask_coverage: Optional[float] = Field(default=None, description="Fraction of image pixels exceeding probability threshold")
    component_count: Optional[int] = Field(default=None, description="Number of disconnected defect regions")
    largest_component_area: Optional[int] = Field(default=None, description="Area (in pixels) of the largest continuous defect")
    metadata: CVModelMetadata

class InspectionContext(BaseModel):
    inspection_id: str
    title: Optional[str] = None

class ElementContext(BaseModel):
    element_id: str
    element_type: str = Field(description="Type of structure, e.g., 'Wall', 'Tunnel', 'Bridge'")
    building_type: Optional[str] = Field(None, description="e.g., 'Commercial', 'Residential'")
    is_load_bearing: bool = Field(default=True, description="Whether the element bears structural load")

class ObservationContext(BaseModel):
    crack_type: str = Field(description="Type of crack observed")
    delay_risk: str = Field(default="low", description="Risk of project delay")

class AnalysisInput(BaseModel):
    inspection: InspectionContext
    element: ElementContext
    observation: ObservationContext
    cv_output: CVOutputContext
    scenario: Optional[str] = Field(default="hairline_crack", description="Scenario identifier for testing")
    image_bytes: Optional[bytes] = Field(default=None, description="Raw image bytes if needed by LLMs directly")
    rag_evidence: Optional[List[RAGEvidence]] = Field(default=None, description="Structured RAG evidence retrieved before analysis")

# --- AI Output Contract ---

class PlanningInformation(BaseModel):
    maintenance_action: Optional[str] = None
    required_workers: Optional[int] = None
    required_materials: Optional[List[str]] = None
    estimated_cost: Optional[str] = None

class ProcessingMetadata(BaseModel):
    processing_time_ms: Optional[int] = None
    agent_steps: Optional[int] = None

class AnalysisResult(BaseModel):
    defect_detected: bool
    defect_probability: float
    condition: Optional[str] = None
    severity: Optional[str] = None
    health_score: Optional[int] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    priority: Optional[str] = None
    max_days: Optional[int] = None
    recommendation: Optional[str] = None
    executive_report: Optional[str] = None
    planning: PlanningInformation = Field(default_factory=PlanningInformation)
    rag_evidence: Optional[List[RAGEvidence]] = Field(default=None, description="Structured RAG evidence used in analysis")
    # Flag so callers can surface a UI notice when no engineering standards were available
    rag_evidence_available: bool = Field(default=True, description="False when RAG returned no evidence; report lacks standards citations")
    processing_metadata: ProcessingMetadata = Field(default_factory=ProcessingMetadata)
    error: Optional[str] = None
