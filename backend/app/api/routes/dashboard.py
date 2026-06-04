from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import BillingRecord, User
from app.schemas.dashboard import DashboardSummary, RecommendationListResponse, RecommendationItem
from app.services.finops import build_dashboard_summary
from app.services.rules_engine import run_rule_engine

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardSummary:
    records = (
        db.query(BillingRecord)
        .order_by(BillingRecord.billed_at.asc())
        .all()
    )
    active_rules, recommendations = run_rule_engine(db, records)
    return build_dashboard_summary(
        records,
        recommendations,
        viewer_name=current_user.full_name,
        active_rule_count=len(active_rules),
    )


@router.get("/recommendations", response_model=RecommendationListResponse)
def list_dashboard_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecommendationListResponse:
    records = (
        db.query(BillingRecord)
        .order_by(BillingRecord.billed_at.asc())
        .all()
    )
    active_rules, recommendations = run_rule_engine(db, records)
    return RecommendationListResponse(
        items=[RecommendationItem.model_validate(item) for item in recommendations],
        active_rule_count=len(active_rules),
        total_open=len(recommendations),
        generated_at=datetime.now(timezone.utc),
    )
