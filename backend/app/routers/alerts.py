"""Alert endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.alert import AlertList, AlertRead
from app.services import alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=AlertList)
def list_alerts(
    unread_only: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return alert_service.list_alerts(db, user.id, unread_only, page, page_size)


@router.put("/{alert_id}/read", response_model=AlertRead)
def mark_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return alert_service.mark_read(db, user.id, alert_id)
