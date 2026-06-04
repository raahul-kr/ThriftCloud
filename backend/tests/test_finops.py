from datetime import datetime

from app.db.models import BillingRecord, CloudProvider
from app.services.finops import build_dashboard_summary


def test_build_dashboard_summary_returns_expected_metrics() -> None:
    records = [
        BillingRecord(
            provider=CloudProvider.aws,
            service_name="EC2",
            region="us-east-1",
            resource_id="aws-1",
            cost=120.0,
            usage_quantity=40,
            is_idle=False,
            billed_at=datetime(2026, 4, 1),
        ),
        BillingRecord(
            provider=CloudProvider.azure,
            service_name="VM",
            region="eastus",
            resource_id="azure-1",
            cost=80.0,
            usage_quantity=30,
            is_idle=True,
            billed_at=datetime(2026, 5, 1),
        ),
    ]

    summary = build_dashboard_summary(records, viewer_name="Tester")

    assert summary.viewer_name == "Tester"
    assert summary.total_cost == 200.0
    assert summary.waste_percentage == 40.0
    assert len(summary.providers) == 2
    assert len(summary.recommendations) >= 1

