"""Alert business logic."""

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.alert import Alert
from app.models.product import Product
from app.schemas.alert import AlertRead


def create_low_stock_alerts(
    db: Session, user_id: int, products: list[Product]
) -> list[int]:
    """Create one unread low_stock alert per low product (deduped). No commit.

    Returns ids of the newly created alerts.
    """
    low = [p for p in products if p.quantity <= p.reorder_level]
    if not low:
        return []
    existing = set(
        db.execute(
            select(Alert.product_id).where(
                Alert.user_id == user_id,
                Alert.type == "low_stock",
                Alert.is_read.is_(False),
                Alert.product_id.in_([p.id for p in low]),
            )
        ).scalars()
    )
    created: list[Alert] = []
    for p in low:
        if p.id in existing:
            continue
        alert = Alert(
            user_id=user_id,
            product_id=p.id,
            type="low_stock",
            message=(
                f"Low stock: '{p.name}' (SKU {p.sku}) has {p.quantity} left "
                f"(reorder level {p.reorder_level})."
            ),
        )
        db.add(alert)
        created.append(alert)
    db.flush()
    return [int(a.id) for a in created]


def _to_read(alert: Alert) -> AlertRead:
    return AlertRead(
        id=alert.id,
        product_id=alert.product_id,
        product_name=alert.product.name if alert.product else None,
        type=alert.type,
        message=alert.message,
        is_read=alert.is_read,
        email_sent=alert.email_sent,
        created_at=alert.created_at,
    )


def list_alerts(
    db: Session, user_id: int, unread_only: bool, page: int, page_size: int
) -> dict:
    filters = [Alert.user_id == user_id]
    if unread_only:
        filters.append(Alert.is_read.is_(False))
    total = db.execute(select(func.count(Alert.id)).where(*filters)).scalar_one()
    unread = db.execute(
        select(func.count(Alert.id)).where(
            Alert.user_id == user_id, Alert.is_read.is_(False)
        )
    ).scalar_one()
    alerts = (
        db.execute(
            select(Alert)
            .where(*filters)
            .order_by(Alert.created_at.desc(), Alert.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    return {
        "items": [_to_read(a) for a in alerts],
        "total": total,
        "page": page,
        "page_size": page_size,
        "unread_count": unread,
    }


def mark_read(db: Session, user_id: int, alert_id: int) -> AlertRead:
    alert = db.execute(
        select(Alert).where(Alert.id == alert_id, Alert.user_id == user_id)
    ).scalar_one_or_none()
    if alert is None:
        raise NotFoundError("Alert")
    if not alert.is_read:
        db.execute(update(Alert).where(Alert.id == alert.id).values(is_read=True))
        db.commit()
        db.refresh(alert)
    return _to_read(alert)
