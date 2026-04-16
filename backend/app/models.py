from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    """Request body for the /api/analyze endpoint."""
    provider: str = Field(..., description="Cloud provider: 'aws' or 'azure'")
    billing_data: Optional[dict[str, float]] = Field(
        default=None,
        description="Optional service-to-cost mapping. Uses sample data if omitted.",
    )


class ServiceBreakdown(BaseModel):
    """Per-service cost breakdown with recommendations."""
    name: str
    cost: float
    category: str
    recommendation: str


class AnalyzeResponse(BaseModel):
    """Response body for analysis endpoints."""
    total_cost: float
    savings_potential: float
    efficiency_score: int = Field(..., ge=0, le=100)
    recommendations: list[str]
    breakdown: list[ServiceBreakdown]
    input_source: str = "sample_data"
    uploaded_file_name: Optional[str] = None
