from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, Boolean, DateTime, Enum as SqlEnum, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class UserRole(str, Enum):
    admin = "admin"
    viewer = "viewer"


class CloudProvider(str, Enum):
    aws = "aws"
    azure = "azure"
    gcp = "gcp"


class RuleCategory(str, Enum):
    idle_cleanup = "idle_cleanup"
    rightsizing = "rightsizing"
    storage_hygiene = "storage_hygiene"
    region_optimization = "region_optimization"


class RecommendationSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RecommendationStatus(str, Enum):
    open = "open"
    resolved = "resolved"
    dismissed = "dismissed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.viewer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive, nullable=False)


class BillingRecord(Base):
    __tablename__ = "billing_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider: Mapped[CloudProvider] = mapped_column(SqlEnum(CloudProvider), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str] = mapped_column(String(60), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    usage_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    is_idle: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    billed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)


class RuleDefinition(Base):
    __tablename__ = "rule_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(600), nullable=False)
    category: Mapped[RuleCategory] = mapped_column(SqlEnum(RuleCategory), nullable=False, index=True)
    severity: Mapped[RecommendationSeverity] = mapped_column(SqlEnum(RecommendationSeverity), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    savings_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    lookback_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    service_filters: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive, onupdate=utc_now_naive, nullable=False)


class RecommendationRecord(Base):
    __tablename__ = "recommendation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recommendation_key: Mapped[str] = mapped_column(String(180), unique=True, nullable=False, index=True)
    rule_key: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    category: Mapped[RuleCategory] = mapped_column(SqlEnum(RuleCategory), nullable=False, index=True)
    status: Mapped[RecommendationStatus] = mapped_column(
        SqlEnum(RecommendationStatus),
        default=RecommendationStatus.open,
        nullable=False,
        index=True,
    )
    severity: Mapped[RecommendationSeverity] = mapped_column(SqlEnum(RecommendationSeverity), nullable=False, index=True)
    provider: Mapped[CloudProvider] = mapped_column(SqlEnum(CloudProvider), nullable=False, index=True)
    service_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    region: Mapped[str | None] = mapped_column(String(60), nullable=True)
    resource_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str] = mapped_column(String(800), nullable=False)
    estimated_monthly_savings: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_annual_savings: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    next_steps: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    assigned_owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive, onupdate=utc_now_naive, nullable=False)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
