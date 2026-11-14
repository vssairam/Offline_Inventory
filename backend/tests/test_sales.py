"""Sale transaction tests (SQLite in-memory; row locks are a no-op there)."""

from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.exceptions import InsufficientStockError, NotFoundError, ValidationFailedError
from app.models.base import Base
from app.models.product import Product
from app.models.user import User
from app.schemas.sale import SaleCreate
from app.services import report_service, sale_service


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    for i in (1, 2):
        session.add(User(id=i, email=f"u{i}@x.com", hashed_password="x"))
    session.add_all(
        [
            Product(
                id=1,
                user_id=1,
                name="Widget",
                sku="W",
                price=Decimal("10.50"),
                cost=Decimal("4.00"),
                quantity=10,
            ),
            Product(
                id=2,
                user_id=1,
                name="=EVIL()",
                sku="E",
                price=Decimal("2.00"),
                cost=Decimal("1.00"),
                quantity=5,
            ),
            Product(
                id=3,
                user_id=1,
                name="Off",
                sku="O",
                price=Decimal(1),
                cost=Decimal(1),
                quantity=5,
                is_active=False,
            ),
            Product(
                id=4,
                user_id=2,
                name="Other",
                sku="X",
                price=Decimal(1),
                cost=Decimal(1),
                quantity=5,
            ),
        ]
    )
    session.commit()
    yield session
    session.close()


def _sale(items):
    return SaleCreate(items=[{"product_id": p, "quantity": q} for p, q in items])


def _qty(db, pid):
    db.expire_all()
    return db.get(Product, pid).quantity


def test_sale_deducts_and_merges(db):
    sale = sale_service.create_sale(db, 1, _sale([(1, 2), (1, 1), (2, 5)]))
    assert sale.total_amount == pytest.approx(41.5)
    assert len(sale.items) == 2
    assert _qty(db, 1) == 7 and _qty(db, 2) == 0
    assert sale.items[0].product_name == "Widget"


def test_insufficient_stock_deducts_nothing(db):
    with pytest.raises(InsufficientStockError):
        sale_service.create_sale(db, 1, _sale([(1, 3), (2, 6)]))
    assert _qty(db, 1) == 10 and _qty(db, 2) == 5


def test_price_snapshot(db):
    sale = sale_service.create_sale(db, 1, _sale([(1, 1)]))
    db.get(Product, 1).price = Decimal(99)
    db.commit()
    assert sale_service.get_sale(db, 1, sale.id).items[0].unit_price == 10.5


def test_ownership_and_inactive(db):
    with pytest.raises(NotFoundError):
        sale_service.create_sale(db, 1, _sale([(4, 1)]))
    with pytest.raises(ValidationFailedError):
        sale_service.create_sale(db, 1, _sale([(3, 1)]))
    assert _qty(db, 4) == 5


def test_sale_scoped_to_user(db):
    sale = sale_service.create_sale(db, 1, _sale([(1, 1)]))
    with pytest.raises(NotFoundError):
        sale_service.get_sale(db, 2, sale.id)
    assert sale_service.list_sales(db, 2, None, None, 1, 20)["total"] == 0


def test_report_and_csv(db):
    sale_service.create_sale(db, 1, _sale([(1, 2), (2, 1)]))
    rep = report_service.sales_report(db, 1, None, None)
    assert rep.total_sales_count == 1
    assert rep.total_revenue == 23.0
    assert rep.total_cost == 9.0
    assert rep.total_profit == 14.0
    assert rep.top_products[0].name == "Widget"
    assert len(rep.daily) == 1 and rep.daily[0].sales_count == 1
    out = "".join(report_service.export_sales_csv(db, 1, None, None))
    assert "'=EVIL()" in out and ",=EVIL()" not in out
