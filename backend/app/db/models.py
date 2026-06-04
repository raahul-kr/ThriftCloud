from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserRole(str, Enum):
    admin = "admin"
    viewer = "viewer"


class CloudProvider(str, Enum):
    aws = "aws"
    azure = "azure"
    gcp = "gcp"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.viewer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


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

