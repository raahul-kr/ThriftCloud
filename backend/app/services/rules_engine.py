from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.models import (
    BillingRecord,
    CloudProvider,
    RecommendationRecord,
    RecommendationSeverity,
    RecommendationStatus,
    RuleCategory,
    RuleDefinition,
    utc_now_naive,
)

SEVERITY_ORDER = {
    RecommendationSeverity.critical: 0,
    RecommendationSeverity.high: 1,
    RecommendationSeverity.medium: 2,
    RecommendationSeverity.low: 3,
}


@dataclass
class EvaluatedRecommendation:
    recommendation_key: str
    rule_key: str
    category: RuleCategory
    provider: CloudProvider
    service_name: str | None
    region: str | None
    resource_count: int
    severity: RecommendationSeverity
    title: str
    description: str
    estimated_monthly_savings: float
    estimated_annual_savings: float
    confidence: float
    evidence: list[str]
    next_steps: list[str]


def _recent_records(records: list[BillingRecord], lookback_days: int) -> list[BillingRecord]:
    if not records:
        return []

    latest_billed_at = max(record.billed_at for record in records)
    cutoff = latest_billed_at - timedelta(days=lookback_days - 1)
    return [record for record in records if record.billed_at >= cutoff]


def _round_currency(value: float) -> float:
    return round(value, 2)


def _confidence(rule: RuleDefinition, cost: float, resource_count: int, signal_bonus: float = 0.0) -> float:
    confidence = rule.confidence_weight + min(0.1, cost / 4000) + min(0.04, resource_count / 40) + signal_bonus
    return min(0.98, round(confidence, 2))


def _title_case_provider(provider: CloudProvider) -> str:
    return provider.value.upper()


def _evaluate_idle_compute(rule: RuleDefinition, records: list[BillingRecord]) -> list[EvaluatedRecommendation]:
    filtered = [
        record
        for record in _recent_records(records, rule.lookback_days)
        if record.is_idle and record.service_name in rule.service_filters
    ]
    grouped: dict[tuple[CloudProvider, str], list[BillingRecord]] = defaultdict(list)
    for record in filtered:
        grouped[(record.provider, record.service_name)].append(record)

    recommendations: list[EvaluatedRecommendation] = []
    for (provider, service_name), group in grouped.items():
        total_cost = sum(item.cost for item in group)
        if total_cost < rule.threshold:
            continue
        region_names = sorted({item.region for item in group})
        resource_count = len(group)
        monthly_savings = _round_currency(total_cost * rule.savings_multiplier)
        recommendations.append(
            EvaluatedRecommendation(
                recommendation_key=f"{rule.key}:{provider.value}:{service_name.lower().replace(' ', '-')}",
                rule_key=rule.key,
                category=rule.category,
                provider=provider,
                service_name=service_name,
                region=region_names[0] if len(region_names) == 1 else None,
                resource_count=resource_count,
                severity=rule.severity,
                title=f"Decommission idle {service_name} capacity",
                description=(
                    f"{resource_count} idle {service_name} resources generated ${total_cost:.2f} in the last "
                    f"{rule.lookback_days} days across {', '.join(region_names)}."
                ),
                estimated_monthly_savings=monthly_savings,
                estimated_annual_savings=_round_currency(monthly_savings * 12),
                confidence=_confidence(rule, total_cost, resource_count, signal_bonus=0.05),
                evidence=[
                    f"Observed idle spend: ${total_cost:.2f}",
                    f"Impacted regions: {', '.join(region_names)}",
                    f"Rule window: {rule.lookback_days} days",
                ],
                next_steps=[
                    "Validate owner and runtime schedule for the idle fleet.",
                    "Stop or delete non-production compute that has no active dependency.",
                    "Move variable workloads behind autoscaling before re-enabling demand.",
                ],
            )
        )
    return recommendations


def _evaluate_db_rightsizing(rule: RuleDefinition, records: list[BillingRecord]) -> list[EvaluatedRecommendation]:
    filtered = [
        record
        for record in _recent_records(records, rule.lookback_days)
        if record.service_name in rule.service_filters and record.usage_quantity <= rule.threshold and record.cost >= 120
    ]
    grouped: dict[tuple[CloudProvider, str], list[BillingRecord]] = defaultdict(list)
    for record in filtered:
        grouped[(record.provider, record.service_name)].append(record)

    recommendations: list[EvaluatedRecommendation] = []
    for (provider, service_name), group in grouped.items():
        total_cost = sum(item.cost for item in group)
        if total_cost < 180:
            continue
        avg_usage = sum(item.usage_quantity for item in group) / len(group)
        monthly_savings = _round_currency(total_cost * rule.savings_multiplier)
        recommendations.append(
            EvaluatedRecommendation(
                recommendation_key=f"{rule.key}:{provider.value}:{service_name.lower().replace(' ', '-')}",
                rule_key=rule.key,
                category=rule.category,
                provider=provider,
                service_name=service_name,
                region=None,
                resource_count=len(group),
                severity=rule.severity,
                title=f"Right-size {service_name} capacity",
                description=(
                    f"{service_name} workloads on {_title_case_provider(provider)} are averaging only "
                    f"{avg_usage:.1f} usage units while spending ${total_cost:.2f} over {rule.lookback_days} days."
                ),
                estimated_monthly_savings=monthly_savings,
                estimated_annual_savings=_round_currency(monthly_savings * 12),
                confidence=_confidence(rule, total_cost, len(group), signal_bonus=max(0.0, (rule.threshold - avg_usage) / 100)),
                evidence=[
                    f"Average observed usage: {avg_usage:.1f} units",
                    f"Estimated rightsizing pool: ${total_cost:.2f}",
                    "Low-utilization database services were clustered by provider and service family.",
                ],
                next_steps=[
                    "Review instance class and storage allocations against actual workload demand.",
                    "Move non-critical databases to smaller tiers or pause schedules where safe.",
                    "Validate reserved capacity assumptions before changing production tiers.",
                ],
            )
        )
    return recommendations


def _evaluate_storage_hygiene(rule: RuleDefinition, records: list[BillingRecord]) -> list[EvaluatedRecommendation]:
    filtered = [
        record
        for record in _recent_records(records, rule.lookback_days)
        if record.service_name in rule.service_filters and (record.is_idle or record.usage_quantity <= rule.threshold)
    ]
    grouped: dict[tuple[CloudProvider, str], list[BillingRecord]] = defaultdict(list)
    for record in filtered:
        grouped[(record.provider, record.service_name)].append(record)

    recommendations: list[EvaluatedRecommendation] = []
    for (provider, service_name), group in grouped.items():
        total_cost = sum(item.cost for item in group)
        if total_cost < 120:
            continue
        monthly_savings = _round_currency(total_cost * rule.savings_multiplier)
        recommendations.append(
            EvaluatedRecommendation(
                recommendation_key=f"{rule.key}:{provider.value}:{service_name.lower().replace(' ', '-')}",
                rule_key=rule.key,
                category=rule.category,
                provider=provider,
                service_name=service_name,
                region=None,
                resource_count=len(group),
                severity=rule.severity,
                title=f"Apply lifecycle policy to {service_name}",
                description=(
                    f"{service_name} on {_title_case_provider(provider)} shows slow-moving or idle storage patterns "
                    f"with ${total_cost:.2f} in spend during the last {rule.lookback_days} days."
                ),
                estimated_monthly_savings=monthly_savings,
                estimated_annual_savings=_round_currency(monthly_savings * 12),
                confidence=_confidence(rule, total_cost, len(group), signal_bonus=0.03),
                evidence=[
                    f"Storage spend in scope: ${total_cost:.2f}",
                    f"Resources flagged: {len(group)}",
                    "Low-activity or idle storage was included in the candidate set.",
                ],
                next_steps=[
                    "Enable tiering or archival policies for cold data.",
                    "Clean orphaned disks, volumes, and unattached snapshots.",
                    "Set retention defaults for non-production environments.",
                ],
            )
        )
    return recommendations


def _evaluate_region_concentration(rule: RuleDefinition, records: list[BillingRecord]) -> list[EvaluatedRecommendation]:
    filtered = _recent_records(records, rule.lookback_days)
    provider_totals: dict[CloudProvider, float] = defaultdict(float)
    region_totals: dict[tuple[CloudProvider, str], float] = defaultdict(float)
    region_counts: dict[tuple[CloudProvider, str], int] = defaultdict(int)

    for record in filtered:
        provider_totals[record.provider] += record.cost
        region_totals[(record.provider, record.region)] += record.cost
        region_counts[(record.provider, record.region)] += 1

    recommendations: list[EvaluatedRecommendation] = []
    for provider, provider_total in provider_totals.items():
        if provider_total < 500:
            continue

        provider_regions = [
            ((candidate_provider, region), total)
            for (candidate_provider, region), total in region_totals.items()
            if candidate_provider == provider
        ]
        if not provider_regions:
            continue

        (candidate_provider, top_region), top_region_cost = max(provider_regions, key=lambda item: item[1])
        share = (top_region_cost / provider_total) * 100
        if share < rule.threshold:
            continue

        monthly_savings = _round_currency(provider_total * rule.savings_multiplier)
        recommendations.append(
            EvaluatedRecommendation(
                recommendation_key=f"{rule.key}:{candidate_provider.value}:{top_region}",
                rule_key=rule.key,
                category=rule.category,
                provider=candidate_provider,
                service_name=None,
                region=top_region,
                resource_count=region_counts[(candidate_provider, top_region)],
                severity=rule.severity,
                title=f"Reduce {_title_case_provider(candidate_provider)} spend concentration in {top_region}",
                description=(
                    f"{share:.1f}% of {_title_case_provider(candidate_provider)} cost is concentrated in {top_region}, "
                    f"which limits optimization options and resilience planning."
                ),
                estimated_monthly_savings=monthly_savings,
                estimated_annual_savings=_round_currency(monthly_savings * 12),
                confidence=_confidence(rule, top_region_cost, region_counts[(candidate_provider, top_region)], signal_bonus=share / 300),
                evidence=[
                    f"Region share: {share:.1f}%",
                    f"Provider spend in window: ${provider_total:.2f}",
                    f"Records clustered in region: {region_counts[(candidate_provider, top_region)]}",
                ],
                next_steps=[
                    "Review whether workloads in the concentrated region should be distributed.",
                    "Check for underused regional reservations and networking overhead.",
                    "Compare unit economics across the secondary regions in your target footprint.",
                ],
            )
        )
    return recommendations


RULE_EVALUATORS = {
    "idle-compute-cleanup": _evaluate_idle_compute,
    "db-rightsizing": _evaluate_db_rightsizing,
    "storage-lifecycle-hygiene": _evaluate_storage_hygiene,
    "region-cost-concentration": _evaluate_region_concentration,
}


def evaluate_rules(records: list[BillingRecord], rules: list[RuleDefinition]) -> list[EvaluatedRecommendation]:
    evaluations: list[EvaluatedRecommendation] = []
    for rule in rules:
        if not rule.active:
            continue
        evaluator = RULE_EVALUATORS.get(rule.key)
        if evaluator is None:
            continue
        evaluations.extend(evaluator(rule, records))
    return evaluations


def _sort_recommendations(recommendations: list[RecommendationRecord]) -> list[RecommendationRecord]:
    return sorted(
        recommendations,
        key=lambda item: (
            SEVERITY_ORDER[item.severity],
            -item.estimated_monthly_savings,
            item.title,
        ),
    )


def run_rule_engine(db: Session, records: list[BillingRecord]) -> tuple[list[RuleDefinition], list[RecommendationRecord]]:
    active_rules = db.query(RuleDefinition).filter(RuleDefinition.active.is_(True)).order_by(RuleDefinition.key.asc()).all()
    evaluations = evaluate_rules(records, active_rules)
    existing_records = {
        recommendation.recommendation_key: recommendation
        for recommendation in db.query(RecommendationRecord).all()
    }
    active_keys = {evaluation.recommendation_key for evaluation in evaluations}
    now = utc_now_naive()

    for evaluation in evaluations:
        recommendation = existing_records.get(evaluation.recommendation_key)
        if recommendation is None:
            recommendation = RecommendationRecord(
                recommendation_key=evaluation.recommendation_key,
                rule_key=evaluation.rule_key,
                category=evaluation.category,
                provider=evaluation.provider,
                service_name=evaluation.service_name,
                region=evaluation.region,
                resource_count=evaluation.resource_count,
                severity=evaluation.severity,
                title=evaluation.title,
                description=evaluation.description,
                estimated_monthly_savings=evaluation.estimated_monthly_savings,
                estimated_annual_savings=evaluation.estimated_annual_savings,
                confidence=evaluation.confidence,
                evidence=evaluation.evidence,
                next_steps=evaluation.next_steps,
                detected_at=now,
                updated_at=now,
            )
            db.add(recommendation)
            existing_records[evaluation.recommendation_key] = recommendation
            continue

        recommendation.rule_key = evaluation.rule_key
        recommendation.category = evaluation.category
        if recommendation.status == RecommendationStatus.dismissed:
            recommendation.provider = evaluation.provider
            recommendation.service_name = evaluation.service_name
            recommendation.region = evaluation.region
            recommendation.resource_count = evaluation.resource_count
            recommendation.severity = evaluation.severity
            recommendation.title = evaluation.title
            recommendation.description = evaluation.description
            recommendation.estimated_monthly_savings = evaluation.estimated_monthly_savings
            recommendation.estimated_annual_savings = evaluation.estimated_annual_savings
            recommendation.confidence = evaluation.confidence
            recommendation.evidence = evaluation.evidence
            recommendation.next_steps = evaluation.next_steps
            recommendation.updated_at = now
            continue

        if recommendation.status == RecommendationStatus.resolved:
            recommendation.status = RecommendationStatus.open
            recommendation.resolved_at = None
            recommendation.acknowledged_at = None

        recommendation.provider = evaluation.provider
        recommendation.service_name = evaluation.service_name
        recommendation.region = evaluation.region
        recommendation.resource_count = evaluation.resource_count
        recommendation.severity = evaluation.severity
        recommendation.title = evaluation.title
        recommendation.description = evaluation.description
        recommendation.estimated_monthly_savings = evaluation.estimated_monthly_savings
        recommendation.estimated_annual_savings = evaluation.estimated_annual_savings
        recommendation.confidence = evaluation.confidence
        recommendation.evidence = evaluation.evidence
        recommendation.next_steps = evaluation.next_steps
        recommendation.updated_at = now
        recommendation.resolved_at = None

    for recommendation in existing_records.values():
        if recommendation.status == RecommendationStatus.dismissed:
            continue
        if recommendation.recommendation_key in active_keys:
            continue
        recommendation.status = RecommendationStatus.resolved
        recommendation.updated_at = now
        recommendation.resolved_at = now

    db.commit()

    open_recommendations = (
        db.query(RecommendationRecord)
        .filter(RecommendationRecord.status == RecommendationStatus.open)
        .all()
    )
    return active_rules, _sort_recommendations(open_recommendations)
