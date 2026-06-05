from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean, pstdev

from app.db.models import BillingRecord
from app.schemas.dashboard import SpendAnomaly, SpendAnomalyResponse


def detect_spend_anomalies(records: list[BillingRecord]) -> SpendAnomalyResponse:
    if not records:
        return SpendAnomalyResponse(items=[], scanned_points=0, generated_at=datetime.now(timezone.utc))

    provider_totals: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for record in records:
        month_label = record.billed_at.strftime("%b %Y")
        provider_totals[record.provider.value.upper()][month_label] += record.cost

    anomalies: list[SpendAnomaly] = []
    scanned_points = 0

    for provider, monthly_costs in provider_totals.items():
        labels = sorted(monthly_costs.keys(), key=lambda label: datetime.strptime(label, "%b %Y"))
        costs = [monthly_costs[label] for label in labels]
        if len(costs) < 3:
            continue

        baseline = mean(costs[:-1])
        spread = pstdev(costs[:-1]) if len(costs[:-1]) > 1 else 0.0
        latest_label = labels[-1]
        latest_cost = costs[-1]
        scanned_points += 1
        threshold = baseline + max(120.0, spread * 1.8)

        if latest_cost <= threshold:
            continue

        deviation = ((latest_cost - baseline) / baseline * 100) if baseline else 0.0
        severity = "high" if deviation >= 35 else "medium"
        anomalies.append(
            SpendAnomaly(
                provider=provider,
                label=latest_label,
                observed_cost=round(latest_cost, 2),
                baseline_cost=round(baseline, 2),
                deviation_percentage=round(deviation, 1),
                severity=severity,
                summary=(
                    f"{provider} spend in {latest_label} is {deviation:.1f}% above the trailing baseline "
                    f"(${baseline:.2f} -> ${latest_cost:.2f})."
                ),
            )
        )

    anomalies.sort(key=lambda item: item.deviation_percentage, reverse=True)
    return SpendAnomalyResponse(
        items=anomalies,
        scanned_points=scanned_points,
        generated_at=datetime.now(timezone.utc),
    )
