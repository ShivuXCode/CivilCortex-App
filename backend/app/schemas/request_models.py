from typing import Optional
from pydantic import BaseModel, Field

class MaintenanceRequest(BaseModel):
    crack_type: str = Field(default="Structural", description="Type of crack observed")
    severity: str = Field(default="medium", description="Severity level: low, medium, high")
    is_load_bearing: bool = Field(default=True, description="Whether the defect is on a load-bearing structure")
    structure_type: str = Field(default="tunnel", description="Type of structure: tunnel, bridge, foundation, etc.")
    delay_risk: str = Field(default="low", description="Risk of project delay: low, medium, high")
    image_bytes: Optional[bytes] = Field(default=None, description="Raw image bytes of the crack")
    scenario: Optional[str] = Field(default="hairline_crack", description="Demo scenario identifier")

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
