"""Dashboard summary (products and sales only)."""

from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale, SaleItem


def _day(value: datetime) -> date:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).date()


def summary(db: Session, user_id: int) -> dict[str, Any]:
    today = datetime.now(UTC).date()
    start_day = today - timedelta(days=29)
    start = datetime(start_day.year, start_day.month, start_day.day, tzinfo=UTC)

    active = (Product.user_id == user_id, Product.is_active.is_(True))
    total_products = db.query(func.count(Product.id)).filter(*active).scalar() or 0
    low = (*active, Product.quantity <= Product.reorder_level)
    low_count = db.query(func.count(Product.id)).filter(*low).scalar() or 0
    stock_value = (
        db.query(func.coalesce(func.sum(Product.quantity * Product.cost), 0))
        .filter(*active)
        .scalar()
    )
    low_items = (
        db.query(Product)
        .filter(*low)
        .order_by((Product.reorder_level - Product.quantity).desc(), Product.id)
        .limit(5)
        .all()
    )

    rows = (
        db.query(Sale.total_amount, Sale.sold_at)
        .filter(Sale.user_id == user_id, Sale.sold_at >= start)
        .all()
    )
    daily: dict[date, float] = defaultdict(float)
    today_count = 0
    revenue_30d = 0.0
    for amount, sold_at in rows:
        d = _day(sold_at)
        if d > today:
            continue
        daily[d] += float(amount)
        revenue_30d += float(amount)
        if d == today:
            today_count += 1
    profit = (
        db.query(
            func.coalesce(
                func.sum(
                    SaleItem.quantity * (SaleItem.unit_price - SaleItem.unit_cost)
                ),
                0,
            )
        )
        .join(Sale, Sale.id == SaleItem.sale_id)
        .filter(Sale.user_id == user_id, Sale.sold_at >= start)
        .scalar()
    )
    trend = [
        {"date": d, "revenue": round(daily.get(d, 0.0), 2)}
        for d in (start_day + timedelta(days=i) for i in range(30))
    ]
    return {
        "total_products": total_products,
        "low_stock_count": low_count,
        "total_stock_value": round(float(stock_value or 0), 2),
        "sales_today_count": today_count,
        "sales_today_revenue": round(daily.get(today, 0.0), 2),
        "revenue_30d": round(revenue_30d, 2),
        "profit_30d": round(float(profit or 0), 2),
        "trend": trend,
        "low_stock_items": [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "quantity": p.quantity,
                "reorder_level": p.reorder_level,
                "deficit": p.reorder_level - p.quantity,
            }
            for p in low_items
        ],
    }
