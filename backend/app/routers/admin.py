"""Admin endpoints (admin only)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.schemas.dashboard import (
    AdminStats,
    AdminUser,
    AdminUserList,
    AdminUserUpdate,
)
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=AdminUserList)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    return admin_service.list_users(db, page, page_size, q)


@router.put("/users/{user_id}", response_model=AdminUser)
def update_user(
    user_id: int,
    body: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return admin_service.update_user(db, admin, user_id, body.is_active, body.is_admin)


@router.get("/stats", response_model=AdminStats)
def get_stats(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return admin_service.stats(db)
