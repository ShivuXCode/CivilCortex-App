from typing import TypedDict, Optional, List

class AgentState(TypedDict, total=False):
    # Inputs
    crack_type: str
    severity: str
    helmet_compliance: float
    delay_risk: str
    is_load_bearing: Optional[bool]
    structure_type: Optional[str]
    image_bytes: Optional[bytes]
    scenario: Optional[str]
    mode: Optional[str]
    mask_coverage: Optional[float]
    component_count: Optional[int]
    largest_component_area: Optional[int]
    
    # Agent Outputs
    crack_detected: Optional[bool]
    crack_probability: Optional[float]
    health_score: Optional[int]
    condition: Optional[str]
    risk_score: Optional[float]
    risk_level: Optional[str]
    priority: Optional[str]
    days: Optional[int]
    maintenance_action: Optional[str]
    required_workers: Optional[int]
    required_materials: Optional[List[str]]
    estimated_cost: Optional[str]
    rag_context: Optional[str]
    rag_evidence: Optional[list]
    recommendation: Optional[str]
