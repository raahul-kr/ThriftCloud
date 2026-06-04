from datetime import datetime

from pydantic import BaseModel


class ProviderSpend(BaseModel):
    provider: str
    total_cost: float
    resource_count: int


class SpendPoint(BaseModel):
    label: str
    total_cost: float


class RecommendationItem(BaseModel):
    title: str
    provider: str
    estimated_savings: float
    confidence: float
    description: str


class DashboardSummary(BaseModel):
    viewer_name: str
    total_cost: float
    monthly_change_percentage: float
    finops_score: int
    waste_percentage: float
    providers: list[ProviderSpend]
    trend: list[SpendPoint]
    recommendations: list[RecommendationItem]
    updated_at: datetime

