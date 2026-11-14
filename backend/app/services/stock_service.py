"""Stock level queries."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.stock import StockItem


def list_stock(
    db: Session,
    user_id: int,
    low_stock: bool,
    q: str | None,
    page: int,
    page_size: int,
) -> dict:
    filters = [Product.user_id == user_id, Product.is_active.is_(True)]
    if low_stock:
        filters.append(Product.quantity <= Product.reorder_level)
    if q:
        like = f"%{q.strip()}%"
        filters.append(Product.name.ilike(like) | Product.sku.ilike(like))
    total = db.execute(select(func.count(Product.id)).where(*filters)).scalar_one()
    rows = (
        db.execute(
            select(Product)
            .where(*filters)
            .order_by(Product.name, Product.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    items = [
        StockItem(
            id=p.id,
            name=p.name,
            sku=p.sku,
            quantity=p.quantity,
            reorder_level=p.reorder_level,
            is_low=p.quantity <= p.reorder_level,
        )
        for p in rows
    ]
    return {"items": items, "total": total, "page": page, "page_size": page_size}
