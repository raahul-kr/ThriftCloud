from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import BillingRecord, User
from app.schemas.dashboard import DashboardSummary
from app.services.finops import build_dashboard_summary

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
    return build_dashboard_summary(records, viewer_name=current_user.full_name)

