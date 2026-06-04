from datetime import datetime

from app.db.models import (
    BillingRecord,
    CloudProvider,
    RecommendationSeverity,
    RuleCategory,
    RuleDefinition,
)
from app.services.rules_engine import evaluate_rules


def test_evaluate_rules_generates_expected_matches() -> None:
    rules = [
        RuleDefinition(
            key="idle-compute-cleanup",
            name="Idle compute cleanup",
            description="Find idle compute.",
            category=RuleCategory.idle_cleanup,
            severity=RecommendationSeverity.high,
            threshold=100,
            confidence_weight=0.84,
            savings_multiplier=0.72,
            lookback_days=30,
            service_filters=["EC2"],
            active=True,
        ),
        RuleDefinition(
            key="db-rightsizing",
            name="Database rightsizing",
            description="Right-size databases.",
            category=RuleCategory.rightsizing,
            severity=RecommendationSeverity.high,
            threshold=30,
            confidence_weight=0.8,
            savings_multiplier=0.38,
            lookback_days=30,
            service_filters=["RDS"],
            active=True,
        ),
    ]

    records = [
        BillingRecord(
            provider=CloudProvider.aws,
            service_name="EC2",
            region="us-east-1",
            resource_id="aws-ec2-idle",
            cost=210.0,
            usage_quantity=18,
            is_idle=True,
            billed_at=datetime(2026, 5, 25),
        ),
        BillingRecord(
            provider=CloudProvider.aws,
            service_name="RDS",
            region="us-east-1",
            resource_id="aws-rds-small",
            cost=240.0,
            usage_quantity=20,
            is_idle=False,
            billed_at=datetime(2026, 5, 26),
        ),
    ]

    evaluations = evaluate_rules(records, rules)
    rule_keys = {evaluation.rule_key for evaluation in evaluations}

    assert "idle-compute-cleanup" in rule_keys
    assert "db-rightsizing" in rule_keys
    assert all(evaluation.estimated_monthly_savings > 0 for evaluation in evaluations)
