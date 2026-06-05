from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.db.models import BillingRecord
from app.schemas.dashboard import ForecastPoint, SpendForecastResponse


def _monthly_totals(records: list[BillingRecord]) -> list[tuple[str, float]]:
    totals: dict[str, float] = defaultdict(float)
    for record in records:
        totals[record.billed_at.strftime("%b %Y")] += record.cost

    return sorted(
        totals.items(),
        key=lambda item: datetime.strptime(item[0], "%b %Y"),
    )


def build_spend_forecast(records: list[BillingRecord], horizon_months: int = 3) -> SpendForecastResponse:
    history = _monthly_totals(records)
    if not history:
        return SpendForecastResponse(
            history=[],
            forecast=[],
            projected_monthly_change_percentage=0.0,
            confidence=0.0,
            method="insufficient_history",
            generated_at=datetime.now(timezone.utc),
        )

    history_points = [ForecastPoint(label=label, total_cost=round(cost, 2), kind="actual") for label, cost in history]
    recent_costs = [cost for _, cost in history[-3:]]
    baseline = sum(recent_costs) / len(recent_costs)
    growth_rate = 0.0
    if len(history) >= 2:
        previous_cost = history[-2][1]
        current_cost = history[-1][1]
        if previous_cost:
            growth_rate = (current_cost - previous_cost) / previous_cost

    last_label, _ = history[-1]
    last_month = datetime.strptime(last_label, "%b %Y")
    forecast_points: list[ForecastPoint] = []
    projected_cost = baseline

    for offset in range(1, horizon_months + 1):
        projected_cost = projected_cost * (1 + (growth_rate * 0.65))
        month_label = (last_month + timedelta(days=32 * offset)).strftime("%b %Y")
        forecast_points.append(
            ForecastPoint(
                label=month_label,
                total_cost=round(projected_cost, 2),
                kind="forecast",
            )
        )

    confidence = min(0.92, 0.55 + min(0.25, len(history) * 0.04) + min(0.12, abs(growth_rate)))

    return SpendForecastResponse(
        history=history_points,
        forecast=forecast_points,
        projected_monthly_change_percentage=round(growth_rate * 100, 1),
        confidence=round(confidence, 2),
        method="deterministic_trend_extrapolation",
        generated_at=datetime.now(timezone.utc),
    )
