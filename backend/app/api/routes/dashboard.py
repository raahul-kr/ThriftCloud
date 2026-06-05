from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import BillingRecord, User
from app.schemas.dashboard import (
    DashboardSummary,
    RecommendationItem,
    RecommendationListResponse,
    RecommendationUpdateRequest,
    RecommendationUpdateResponse,
    SpendAnomalyResponse,
    SpendForecastResponse,
)
from app.services.anomalies import detect_spend_anomalies
from app.services.finops import build_dashboard_summary
from app.services.forecasting import build_spend_forecast
from app.services.recommendations import update_recommendation
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


@router.get("/forecast", response_model=SpendForecastResponse)
def get_spend_forecast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SpendForecastResponse:
    records = db.query(BillingRecord).order_by(BillingRecord.billed_at.asc()).all()
    return build_spend_forecast(records)


@router.get("/anomalies", response_model=SpendAnomalyResponse)
def get_spend_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SpendAnomalyResponse:
    records = db.query(BillingRecord).order_by(BillingRecord.billed_at.asc()).all()
    return detect_spend_anomalies(records)


@router.patch("/recommendations/{recommendation_id}", response_model=RecommendationUpdateResponse)
def update_dashboard_recommendation(
    recommendation_id: int,
    payload: RecommendationUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecommendationUpdateResponse:
    recommendation = update_recommendation(
        db,
        recommendation_id,
        payload.action,
        current_user,
        assigned_owner=payload.assigned_owner,
    )
    messages = {
        "acknowledge": "Recommendation acknowledged",
        "dismiss": "Recommendation dismissed",
        "assign_owner": f"Owner assigned to {recommendation.assigned_owner}",
        "resolve": "Recommendation marked as resolved",
    }
    return RecommendationUpdateResponse(
        item=RecommendationItem.model_validate(recommendation),
        message=messages[payload.action.value],
    )
