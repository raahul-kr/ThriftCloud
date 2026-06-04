from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProviderSpend(BaseModel):
    provider: str
    total_cost: float
    resource_count: int


class SpendPoint(BaseModel):
    label: str
    total_cost: float


class RecommendationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recommendation_key: str
    rule_key: str
    category: str
    status: str
    severity: str
    title: str
    provider: str
    service_name: str | None = None
    region: str | None = None
    resource_count: int
    estimated_monthly_savings: float
    estimated_annual_savings: float
    confidence: float
    description: str
    evidence: list[str]
    next_steps: list[str]
    detected_at: datetime


class DashboardSummary(BaseModel):
    viewer_name: str
    total_cost: float
    monthly_change_percentage: float
    finops_score: int
    waste_percentage: float
    active_rule_count: int
    triggered_rule_count: int
    open_recommendation_count: int
    potential_monthly_savings: float
    potential_annual_savings: float
    providers: list[ProviderSpend]
    trend: list[SpendPoint]
    recommendations: list[RecommendationItem]
    updated_at: datetime


class RecommendationListResponse(BaseModel):
    items: list[RecommendationItem]
    active_rule_count: int
    total_open: int
    generated_at: datetime
