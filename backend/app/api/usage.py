from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User, UsageRecord, GenerationJob
from app.schemas.schemas import UsageResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/usage", tags=["Usage"])

@router.get("", response_model=UsageResponse)
def get_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total_generations = db.query(GenerationJob).filter(
        GenerationJob.user_id == current_user.id
    ).count()

    records = db.query(UsageRecord).filter(
        UsageRecord.user_id == current_user.id
    ).order_by(UsageRecord.created_at.desc()).limit(20).all()

    history = [
        {
            "id": r.id,
            "credits_spent": r.credits_spent,
            "action": r.action,
            "created_at": r.created_at.isoformat(),
        }
        for r in records
    ]

    return UsageResponse(
        credits_balance=current_user.credits_balance,
        plan=current_user.plan,
        total_generations=total_generations,
        history=history,
    )
