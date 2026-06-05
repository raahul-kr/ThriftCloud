from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import RecommendationRecord, RecommendationStatus, User, UserRole, utc_now_naive
from app.schemas.dashboard import RecommendationAction


def update_recommendation(
    db: Session,
    recommendation_id: int,
    action: RecommendationAction,
    current_user: User,
    assigned_owner: str | None = None,
) -> RecommendationRecord:
    recommendation = db.query(RecommendationRecord).filter(RecommendationRecord.id == recommendation_id).first()
    if recommendation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")

    now = utc_now_naive()

    if action == RecommendationAction.acknowledge:
        if recommendation.status != RecommendationStatus.open:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only open recommendations can be acknowledged",
            )
        recommendation.acknowledged_at = now
        recommendation.updated_at = now
    elif action == RecommendationAction.dismiss:
        if recommendation.status != RecommendationStatus.open:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only open recommendations can be dismissed",
            )
        recommendation.status = RecommendationStatus.dismissed
        recommendation.updated_at = now
    elif action == RecommendationAction.assign_owner:
        if current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can assign recommendation owners",
            )
        owner = (assigned_owner or "").strip()
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="assigned_owner is required for assign_owner action",
            )
        recommendation.assigned_owner = owner
        recommendation.updated_at = now
    elif action == RecommendationAction.resolve:
        if recommendation.status != RecommendationStatus.open:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only open recommendations can be resolved",
            )
        recommendation.status = RecommendationStatus.resolved
        recommendation.resolved_at = now
        recommendation.updated_at = now
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported action")

    db.commit()
    db.refresh(recommendation)
    return recommendation
