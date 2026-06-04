from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from app.db.models import BillingRecord
from app.schemas.dashboard import DashboardSummary, ProviderSpend, RecommendationItem, SpendPoint


def build_dashboard_summary(records: list[BillingRecord], viewer_name: str) -> DashboardSummary:
    if not records:
        return DashboardSummary(
            viewer_name=viewer_name,
            total_cost=0,
            monthly_change_percentage=0,
            finops_score=100,
            waste_percentage=0,
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
    service_waste: dict[tuple[str, str], float] = defaultdict(float)

    for record in records:
        provider_key = record.provider.value.upper()
        provider_costs[provider_key] += record.cost
        provider_counts[provider_key] += 1
        trend_costs[record.billed_at.strftime("%b %Y")] += record.cost
        if record.is_idle:
            service_waste[(provider_key, record.service_name)] += record.cost

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
    diversification_score = 70 + min(30, len(provider_costs) * 10)
    finops_score = round((utilization_score * 0.5) + (hygiene_score * 0.3) + (diversification_score * 0.2))

    recommendations = [
        RecommendationItem(
            title=f"Review {service} waste on {provider}",
            provider=provider,
            estimated_savings=round(cost, 2),
            confidence=min(0.95, round(0.62 + (cost / max(total_cost, 1)), 2)),
            description=f"Idle or underutilized {service} resources are driving avoidable spend on {provider}.",
        )
        for (provider, service), cost in sorted(service_waste.items(), key=lambda item: item[1], reverse=True)[:3]
    ]

    if not recommendations:
        recommendations.append(
            RecommendationItem(
                title="Healthy cloud posture detected",
                provider="MULTI",
                estimated_savings=0,
                confidence=0.88,
                description="No high-confidence waste clusters were detected in the current seeded dataset.",
            )
        )

    return DashboardSummary(
        viewer_name=viewer_name,
        total_cost=total_cost,
        monthly_change_percentage=monthly_change,
        finops_score=finops_score,
        waste_percentage=waste_percentage,
        providers=providers,
        trend=trend,
        recommendations=recommendations,
        updated_at=datetime.now(timezone.utc),
    )
