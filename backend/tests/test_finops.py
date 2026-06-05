from datetime import datetime

from app.db.models import (
    BillingRecord,
    CloudProvider,
    RecommendationRecord,
    RecommendationSeverity,
    RecommendationStatus,
    RuleCategory,
)
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

    recommendations = [
        RecommendationRecord(
            id=1,
            recommendation_key="idle-compute-cleanup:azure:vm",
            rule_key="idle-compute-cleanup",
            category=RuleCategory.idle_cleanup,
            status=RecommendationStatus.open,
            severity=RecommendationSeverity.high,
            provider=CloudProvider.azure,
            service_name="VM",
            region="eastus",
            resource_count=1,
            title="Decommission idle VM capacity",
            description="A seeded idle VM recommendation.",
            estimated_monthly_savings=57.6,
            estimated_annual_savings=691.2,
            confidence=0.9,
            evidence=["Observed idle spend: $80.00"],
            next_steps=["Stop or delete unused compute."],
            detected_at=datetime(2026, 5, 1),
            updated_at=datetime(2026, 5, 1),
        )
    ]

    summary = build_dashboard_summary(
        records,
        recommendations,
        viewer_name="Tester",
        active_rule_count=4,
    )

    assert summary.viewer_name == "Tester"
    assert summary.total_cost == 200.0
    assert summary.waste_percentage == 40.0
    assert len(summary.providers) == 2
    assert summary.active_rule_count == 4
    assert summary.open_recommendation_count == 1
    assert summary.potential_monthly_savings == 57.6
    assert len(summary.recommendations) == 1
