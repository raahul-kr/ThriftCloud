from datetime import datetime

from app.db.models import BillingRecord, CloudProvider
from app.services.anomalies import detect_spend_anomalies
from app.services.forecasting import build_spend_forecast


def test_build_spend_forecast_returns_projections() -> None:
    records = [
        BillingRecord(
            provider=CloudProvider.aws,
            service_name="EC2",
            region="us-east-1",
            resource_id=f"aws-{index}",
            cost=100 + index * 10,
            usage_quantity=40,
            is_idle=False,
            billed_at=datetime(2026, index, 1),
        )
        for index in range(1, 5)
    ]

    forecast = build_spend_forecast(records, horizon_months=2)

    assert len(forecast.history) == 4
    assert len(forecast.forecast) == 2
    assert forecast.method == "deterministic_trend_extrapolation"
    assert forecast.confidence > 0


def test_detect_spend_anomalies_flags_spike() -> None:
    records = [
        BillingRecord(
            provider=CloudProvider.aws,
            service_name="EC2",
            region="us-east-1",
            resource_id=f"aws-{index}",
            cost=100.0,
            usage_quantity=40,
            is_idle=False,
            billed_at=datetime(2026, index, 1),
        )
        for index in range(1, 4)
    ]
    records.append(
        BillingRecord(
            provider=CloudProvider.aws,
            service_name="EC2",
            region="us-east-1",
            resource_id="aws-spike",
            cost=260.0,
            usage_quantity=40,
            is_idle=False,
            billed_at=datetime(2026, 4, 1),
        )
    )

    anomalies = detect_spend_anomalies(records)

    assert anomalies.scanned_points == 1
    assert len(anomalies.items) == 1
    assert anomalies.items[0].provider == "AWS"
    assert anomalies.items[0].severity in {"medium", "high"}
