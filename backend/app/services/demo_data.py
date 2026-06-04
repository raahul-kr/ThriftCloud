from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.models import (
    BillingRecord,
    CloudProvider,
    RecommendationSeverity,
    RuleCategory,
    RuleDefinition,
    User,
    UserRole,
)

PROVIDER_SERVICES: dict[CloudProvider, list[str]] = {
    CloudProvider.aws: ["EC2", "RDS", "S3", "EBS", "CloudFront"],
    CloudProvider.azure: ["VM", "SQL Database", "Blob Storage", "Disk", "Functions"],
    CloudProvider.gcp: ["Compute Engine", "Cloud SQL", "Cloud Storage", "Persistent Disk", "BigQuery"],
}

REGIONS = {
    CloudProvider.aws: ["us-east-1", "ap-south-1"],
    CloudProvider.azure: ["eastus", "centralindia"],
    CloudProvider.gcp: ["us-central1", "asia-south1"],
}

DEFAULT_RULES = [
    {
        "key": "idle-compute-cleanup",
        "name": "Idle compute cleanup",
        "description": "Finds idle compute resources that can usually be stopped or decommissioned quickly.",
        "category": RuleCategory.idle_cleanup,
        "severity": RecommendationSeverity.high,
        "threshold": 140.0,
        "confidence_weight": 0.84,
        "savings_multiplier": 0.72,
        "lookback_days": 30,
        "service_filters": ["EC2", "VM", "Compute Engine"],
    },
    {
        "key": "db-rightsizing",
        "name": "Database rightsizing",
        "description": "Flags expensive database services that show low sustained usage in the seeded dataset.",
        "category": RuleCategory.rightsizing,
        "severity": RecommendationSeverity.high,
        "threshold": 30.0,
        "confidence_weight": 0.8,
        "savings_multiplier": 0.38,
        "lookback_days": 30,
        "service_filters": ["RDS", "SQL Database", "Cloud SQL"],
    },
    {
        "key": "storage-lifecycle-hygiene",
        "name": "Storage lifecycle hygiene",
        "description": "Highlights storage services that should move to lifecycle, archive, or cleanup policies.",
        "category": RuleCategory.storage_hygiene,
        "severity": RecommendationSeverity.medium,
        "threshold": 36.0,
        "confidence_weight": 0.76,
        "savings_multiplier": 0.29,
        "lookback_days": 30,
        "service_filters": ["S3", "Blob Storage", "Cloud Storage", "Persistent Disk", "EBS"],
    },
    {
        "key": "region-cost-concentration",
        "name": "Region cost concentration",
        "description": "Detects when a single region dominates a provider footprint and creates optimization risk.",
        "category": RuleCategory.region_optimization,
        "severity": RecommendationSeverity.medium,
        "threshold": 55.0,
        "confidence_weight": 0.7,
        "savings_multiplier": 0.12,
        "lookback_days": 30,
        "service_filters": [],
    },
]


def seed_database(db: Session) -> None:
    demo_users = [
        {
            "email": "admin@thriftcloud.dev",
            "full_name": "ThriftCloud Admin",
            "role": UserRole.admin,
        },
        {
            "email": "viewer@thriftcloud.dev",
            "full_name": "FinOps Viewer",
            "role": UserRole.viewer,
        },
    ]

    users_to_create: list[User] = []
    for demo_user in demo_users:
        exists = db.query(User).filter(User.email == demo_user["email"]).first()
        if exists:
            continue
        users_to_create.append(
            User(
                email=demo_user["email"],
                full_name=demo_user["full_name"],
                hashed_password=get_password_hash("demo12345"),
                role=demo_user["role"],
            )
        )

    if users_to_create:
        db.add_all(users_to_create)
        db.commit()

    rules_to_create: list[RuleDefinition] = []
    for rule in DEFAULT_RULES:
        exists = db.query(RuleDefinition).filter(RuleDefinition.key == rule["key"]).first()
        if exists:
            continue
        rules_to_create.append(RuleDefinition(**rule))

    if rules_to_create:
        db.add_all(rules_to_create)
        db.commit()

    if db.query(BillingRecord).first():
        return

    random.seed(42)
    today = datetime.now(timezone.utc).replace(tzinfo=None, hour=0, minute=0, second=0, microsecond=0)
    records: list[BillingRecord] = []

    for day_offset in range(90):
        billed_at = today - timedelta(days=89 - day_offset)
        for provider in CloudProvider:
            service = random.choice(PROVIDER_SERVICES[provider])
            region = random.choice(REGIONS[provider])
            cost = round(random.uniform(40, 380), 2)
            is_idle = random.random() < 0.16
            if is_idle:
                cost = round(cost * random.uniform(0.55, 0.82), 2)

            records.append(
                BillingRecord(
                    provider=provider,
                    service_name=service,
                    region=region,
                    resource_id=f"{provider.value}-{day_offset}-{service.lower().replace(' ', '-')}",
                    cost=cost,
                    usage_quantity=round(random.uniform(8, 96), 2),
                    is_idle=is_idle,
                    billed_at=billed_at,
                )
            )

    db.add_all(records)
    db.commit()
