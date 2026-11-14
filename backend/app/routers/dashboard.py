"""Dashboard endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.dashboard import DashboardSummary
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return dashboard_service.summary(db, user.id)
