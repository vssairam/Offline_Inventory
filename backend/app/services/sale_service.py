"""Sale business logic: atomic stock deduction and queries."""

from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from fastapi import BackgroundTasks
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.exceptions import InsufficientStockError, NotFoundError, ValidationFailedError
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.schemas.sale import SaleCreate, SaleItemRead, SaleRead
from app.services import alert_service, email_service


def after_stock_change(db: Session, user_id: int, products: list[Product]) -> list[int]:
    """HOOK: called inside the sale transaction after stock was deducted.

    Creates deduped low-stock alerts (no commit). Returns new alert ids so the
    caller can email them after the commit.
    """
    return alert_service.create_low_stock_alerts(db, user_id, products)


def create_sale(
    db: Session,
    user_id: int,
    data: SaleCreate,
    background_tasks: BackgroundTasks | None = None,
) -> SaleRead:
    # Merge duplicate product lines.
    wanted: dict[int, int] = defaultdict(int)
    for line in data.items:
        wanted[line.product_id] += line.quantity
    if not wanted:
        raise ValidationFailedError("A sale needs at least one item")

    try:
        ids = sorted(wanted)  # consistent lock order avoids deadlocks
        rows = (
            db.execute(
                select(Product)
                .where(Product.id.in_(ids), Product.user_id == user_id)
                .order_by(Product.id)
                .with_for_update()
            )
            .scalars()
            .all()
        )
        products = {p.id: p for p in rows}

        before = {pid: p.quantity for pid, p in products.items()}
        total = Decimal(0)
        sale = Sale(user_id=user_id, total_amount=Decimal(0))
        if data.sold_at is not None:
            sale.sold_at = data.sold_at
        for pid in ids:
            product = products.get(pid)
            if product is None:
                raise NotFoundError(f"Product {pid}")
            if not product.is_active:
                raise ValidationFailedError(f"Product '{product.name}' is inactive")
            qty = wanted[pid]
            if product.quantity < qty:
                raise InsufficientStockError(
                    f"Insufficient stock for '{product.name}': "
                    f"available {product.quantity}, requested {qty}"
                )
            product.quantity -= qty
            total += Decimal(product.price) * qty
            sale.items.append(
                SaleItem(
                    product_id=pid,
                    quantity=qty,
                    unit_price=product.price,
                    unit_cost=product.cost,
                )
            )
        sale.total_amount = total.quantize(Decimal("0.01"))
        db.add(sale)
        db.flush()
        # Alert only on a downward threshold crossing, not on every sale while still low.
        crossed = [products[i] for i in ids if before[i] > products[i].reorder_level]
        alert_ids = after_stock_change(db, user_id, crossed)
        db.commit()
    except Exception:
        db.rollback()
        raise
    if alert_ids:  # after commit; email problems must never fail the sale
        if background_tasks is not None:
            background_tasks.add_task(email_service.send_alert_emails, alert_ids)
        else:
            email_service.send_alert_emails_in_thread(alert_ids)
    return get_sale(db, user_id, sale.id)


def _to_read(sale: Sale) -> SaleRead:
    items = [
        SaleItemRead(
            id=i.id,
            product_id=i.product_id,
            product_name=i.product.name if i.product else None,
            quantity=i.quantity,
            unit_price=float(i.unit_price),
            unit_cost=float(i.unit_cost),
            line_total=float(Decimal(i.unit_price) * i.quantity),
        )
        for i in sale.items
    ]
    return SaleRead(
        id=sale.id,
        total_amount=float(sale.total_amount),
        sold_at=sale.sold_at,
        created_at=sale.created_at,
        item_count=sum(i.quantity for i in sale.items),
        items=items,
    )


def get_sale(db: Session, user_id: int, sale_id: int) -> SaleRead:
    sale = db.execute(
        select(Sale)
        .where(Sale.id == sale_id, Sale.user_id == user_id)
        .options(selectinload(Sale.items).selectinload(SaleItem.product))
        .execution_options(populate_existing=True)
    ).scalar_one_or_none()
    if sale is None:
        raise NotFoundError("Sale")
    return _to_read(sale)


def list_sales(
    db: Session,
    user_id: int,
    date_from: datetime | None,
    date_to: datetime | None,
    page: int,
    page_size: int,
) -> dict:
    filters = [Sale.user_id == user_id]
    if date_from is not None:
        filters.append(Sale.sold_at >= date_from)
    if date_to is not None:
        filters.append(Sale.sold_at <= date_to)
    total = db.execute(select(func.count(Sale.id)).where(*filters)).scalar_one()
    sales = (
        db.execute(
            select(Sale)
            .where(*filters)
            .options(selectinload(Sale.items).selectinload(SaleItem.product))
            .order_by(Sale.sold_at.desc(), Sale.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .scalars()
        .all()
    )
    return {
        "items": [_to_read(s) for s in sales],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
