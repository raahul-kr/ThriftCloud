from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from app.db.models import BillingRecord, RecommendationRecord
from app.schemas.dashboard import DashboardSummary, RecommendationItem, ProviderSpend, SpendPoint


def build_dashboard_summary(
    records: list[BillingRecord],
    recommendations: list[RecommendationRecord],
    viewer_name: str,
    active_rule_count: int,
) -> DashboardSummary:
    if not records:
        return DashboardSummary(
            viewer_name=viewer_name,
            total_cost=0,
            monthly_change_percentage=0,
            finops_score=100,
            waste_percentage=0,
            active_rule_count=active_rule_count,
            triggered_rule_count=0,
            open_recommendation_count=0,
            potential_monthly_savings=0,
            potential_annual_savings=0,
            providers=[],
            trend=[],
            recommendations=[],
            updated_at=datetime.now(timezone.utc),
        )

    total_cost = round(sum(record.cost for record in records), 2)
    idle_cost = round(sum(record.cost for record in records if record.is_idle), 2)
    waste_percentage = round((idle_cost / total_cost) * 100, 1) if total_cost else 0

    provider_costs: dict[str, float] = defaultdict(float)
    provider_counts: dict[str, int] = defaultdict(int)
    trend_costs: dict[str, float] = defaultdict(float)
    for record in records:
        provider_key = record.provider.value.upper()
        provider_costs[provider_key] += record.cost
        provider_counts[provider_key] += 1
        trend_costs[record.billed_at.strftime("%b %Y")] += record.cost

    providers = [
        ProviderSpend(
            provider=provider,
            total_cost=round(cost, 2),
            resource_count=provider_counts[provider],
        )
        for provider, cost in sorted(provider_costs.items())
    ]

    trend = [
        SpendPoint(label=label, total_cost=round(cost, 2))
        for label, cost in sorted(
            trend_costs.items(),
            key=lambda item: datetime.strptime(item[0], "%b %Y"),
        )
    ]

    current_month_cost = trend[-1].total_cost if trend else 0
    previous_month_cost = trend[-2].total_cost if len(trend) > 1 else current_month_cost
    monthly_change = 0.0
    if previous_month_cost:
        monthly_change = round(((current_month_cost - previous_month_cost) / previous_month_cost) * 100, 1)

    utilization_score = max(0, round(100 - waste_percentage))
    hygiene_score = max(0, round(100 - (len([r for r in records if r.is_idle]) / len(records)) * 120))
    automation_score = 60 + min(40, active_rule_count * 10)
    recommendation_pressure = min(18, len(recommendations) * 3)
    finops_score = round(
        (utilization_score * 0.45)
        + (hygiene_score * 0.25)
        + (automation_score * 0.2)
        + (max(0, 100 - recommendation_pressure) * 0.1)
    )

    recommendation_items = [RecommendationItem.model_validate(item) for item in recommendations[:5]]
    triggered_rule_count = len({item.rule_key for item in recommendations})
    potential_monthly_savings = round(sum(item.estimated_monthly_savings for item in recommendations), 2)
    potential_annual_savings = round(sum(item.estimated_annual_savings for item in recommendations), 2)

    return DashboardSummary(
        viewer_name=viewer_name,
        total_cost=total_cost,
        monthly_change_percentage=monthly_change,
        finops_score=finops_score,
        waste_percentage=waste_percentage,
        active_rule_count=active_rule_count,
        triggered_rule_count=triggered_rule_count,
        open_recommendation_count=len(recommendations),
        potential_monthly_savings=potential_monthly_savings,
        potential_annual_savings=potential_annual_savings,
        providers=providers,
        trend=trend,
        recommendations=recommendation_items,
        updated_at=datetime.now(timezone.utc),
    )
