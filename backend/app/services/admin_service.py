"""Admin user management and platform stats."""

from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models.product import Product
from app.models.sale import Sale
from app.models.user import User
from app.services.auth_service import revoke_all_refresh_tokens


def list_users(db: Session, page: int, page_size: int, q: str | None) -> dict[str, Any]:
    query = db.query(User)
    if q:
        like = f"%{q.strip().lower()}%"
        query = query.filter(
            func.lower(User.email).like(like)
            | func.lower(func.coalesce(User.full_name, "")).like(like)
        )
    total = query.count()
    items = (
        query.order_by(User.id).offset((page - 1) * page_size).limit(page_size).all()
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def update_user(
    db: Session,
    admin: Any,
    user_id: int,
    is_active: bool | None,
    is_admin: bool | None,
) -> User:
    user = db.get(User, user_id)
    if not user:
        raise NotFoundError("User")
    if user.id == admin.id and (is_active is False or is_admin is False):
        raise ConflictError("Admins cannot deactivate or demote themselves")
    if is_active is not None:
        user.is_active = is_active
        if not is_active:
            revoke_all_refresh_tokens(db, user.id)  # deactivation ends all sessions
    if is_admin is not None:
        user.is_admin = is_admin
    db.commit()
    db.refresh(user)
    return user


def stats(db: Session) -> dict[str, Any]:
    active = db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar()
    revenue = db.query(func.coalesce(func.sum(Sale.total_amount), 0)).scalar()
    return {
        "total_users": db.query(func.count(User.id)).scalar() or 0,
        "active_users": active or 0,
        "total_products": db.query(func.count(Product.id)).scalar() or 0,
        "total_sales": db.query(func.count(Sale.id)).scalar() or 0,
        "total_revenue": round(float(revenue or 0), 2),
    }
