"""Sales reporting and CSV export."""

import csv
import io
from collections.abc import Iterator
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.exceptions import ValidationFailedError
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.schemas.sale import DailyPoint, SalesReport, TopProduct

MAX_EXPORT_ROWS = 50_000


def _filters(user_id: int, date_from: datetime | None, date_to: datetime | None):
    f = [Sale.user_id == user_id]
    if date_from is not None:
        f.append(Sale.sold_at >= date_from)
    if date_to is not None:
        f.append(Sale.sold_at <= date_to)
    return f


def _dec(v: object) -> Decimal:
    return Decimal(str(v if v is not None else 0))


def sales_report(
    db: Session, user_id: int, date_from: datetime | None, date_to: datetime | None
) -> SalesReport:
    f = _filters(user_id, date_from, date_to)
    revenue_expr = func.coalesce(func.sum(SaleItem.quantity * SaleItem.unit_price), 0)
    cost_expr = func.coalesce(func.sum(SaleItem.quantity * SaleItem.unit_cost), 0)

    count = db.execute(select(func.count(Sale.id)).where(*f)).scalar_one()
    rev_raw, cost_raw = db.execute(
        select(revenue_expr, cost_expr)
        .select_from(SaleItem)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .where(*f)
    ).one()
    rev, cost = _dec(rev_raw), _dec(cost_raw)

    top_rows = db.execute(
        select(
            SaleItem.product_id,
            Product.name,
            func.sum(SaleItem.quantity).label("qty"),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label("rev"),
        )
        .join(Sale, Sale.id == SaleItem.sale_id)
        .join(Product, Product.id == SaleItem.product_id)
        .where(*f)
        .group_by(SaleItem.product_id, Product.name)
        .order_by(func.sum(SaleItem.quantity).desc(), SaleItem.product_id)
        .limit(10)
    ).all()

    day = func.date(Sale.sold_at)
    daily_rows = db.execute(
        select(
            day.label("d"),
            func.count(func.distinct(Sale.id)),
            revenue_expr,
            cost_expr,
        )
        .select_from(SaleItem)
        .join(Sale, Sale.id == SaleItem.sale_id)
        .where(*f)
        .group_by(day)
        .order_by(day)
    ).all()

    return SalesReport(
        total_sales_count=count,
        total_revenue=float(rev),
        total_cost=float(cost),
        total_profit=float(rev - cost),
        top_products=[
            TopProduct(
                product_id=r[0],
                name=r[1],
                quantity=int(r[2]),
                revenue=float(_dec(r[3])),
            )
            for r in top_rows
        ],
        daily=[
            DailyPoint(
                date=str(r[0]),
                sales_count=int(r[1]),
                revenue=float(_dec(r[2])),
                profit=float(_dec(r[2]) - _dec(r[3])),
            )
            for r in daily_rows
        ],
    )


def csv_safe(value: object) -> str:
    """Neutralise CSV/Excel formula injection by prefixing a single quote."""
    s = "" if value is None else str(value)
    if s and (s[0] in ("\t", "\r", "\n") or s.lstrip()[:1] in ("=", "+", "-", "@")):
        return "'" + s
    return s


def _row(values: list[object]) -> str:
    buf = io.StringIO()
    csv.writer(buf).writerow(values)
    return buf.getvalue()


def export_sales_csv(
    db: Session, user_id: int, date_from: datetime | None, date_to: datetime | None
) -> Iterator[str]:
    f = _filters(user_id, date_from, date_to)
    stmt = (
        select(
            Sale.id,
            Sale.sold_at,
            Product.name,
            SaleItem.quantity,
            SaleItem.unit_price,
            SaleItem.unit_cost,
        )
        .join(SaleItem, SaleItem.sale_id == Sale.id)
        .join(Product, Product.id == SaleItem.product_id)
        .where(*f)
        .order_by(Sale.sold_at, Sale.id, SaleItem.id)
        .limit(MAX_EXPORT_ROWS + 1)
    )
    yield _row(
        [
            "sale_id",
            "sold_at",
            "product",
            "quantity",
            "unit_price",
            "unit_cost",
            "line_total",
            "line_profit",
        ]
    )
    for count, (sid, sold_at, name, qty, price, cost) in enumerate(db.execute(stmt), 1):
        if count > MAX_EXPORT_ROWS:
            raise ValidationFailedError(
                f"Export exceeds {MAX_EXPORT_ROWS} rows; narrow the date range"
            )
        price, cost = Decimal(price), Decimal(cost)
        yield _row(
            [
                sid,
                sold_at.isoformat(),
                csv_safe(name),
                qty,
                price,
                cost,
                price * qty,
                (price - cost) * qty,
            ]
        )
