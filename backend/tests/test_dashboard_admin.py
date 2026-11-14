"""Dashboard and admin endpoint tests (SQLite in-memory, dependency overrides)."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.dependencies import get_current_user, get_db
from app.main import app
from app.models.base import Base
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.user import User


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(User(id=1, email="admin@x.com", hashed_password="x", is_admin=True))
    session.add(User(id=2, email="u2@x.com", hashed_password="x", full_name="Bob"))
    session.add(User(id=3, email="u3@x.com", hashed_password="x"))
    session.commit()
    yield session
    session.close()


@pytest.fixture
def client(db):
    state = {"uid": 1}

    def _db():
        yield db

    def _user():
        return db.get(User, state["uid"])

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_current_user] = _user
    c = TestClient(app)
    c.state = state  # type: ignore[attr-defined]
    yield c
    app.dependency_overrides.clear()


def _product(uid, pid, sku, qty, reorder, cost="2.00", active=True):
    return Product(
        id=pid,
        user_id=uid,
        name=f"P{pid}",
        sku=sku,
        price=Decimal("5.00"),
        cost=Decimal(cost),
        quantity=qty,
        reorder_level=reorder,
        is_active=active,
    )


def _sale(db, uid, sid, when, pid, qty, price="5.00", cost="2.00"):
    amount = Decimal(price) * qty
    db.add(Sale(id=sid, user_id=uid, total_amount=amount, sold_at=when))
    db.add(
        SaleItem(
            sale_id=sid,
            product_id=pid,
            quantity=qty,
            unit_price=Decimal(price),
            unit_cost=Decimal(cost),
        )
    )


def test_dashboard_numbers_and_isolation(client, db):
    now = datetime.now(UTC)
    db.add_all(
        [
            _product(2, 1, "A", 1, 5),  # low, deficit 4, value 2
            _product(2, 2, "B", 10, 2),  # ok, value 20
            _product(2, 3, "C", 0, 3, active=False),  # inactive: ignored
            _product(3, 4, "D", 0, 9),  # other user
        ]
    )
    db.flush()
    _sale(db, 2, 1, now, 1, 2)  # 10 revenue, 6 profit
    _sale(db, 2, 2, now - timedelta(days=3), 2, 1)  # 5, 3
    _sale(db, 2, 3, now - timedelta(days=45), 2, 4)  # outside window
    _sale(db, 3, 4, now, 4, 7)  # other user
    db.commit()

    client.state["uid"] = 2
    r = client.get("/api/v1/dashboard/summary")
    assert r.status_code == 200
    d = r.json()
    assert d["total_products"] == 2
    assert d["low_stock_count"] == 1
    assert d["total_stock_value"] == 22.0
    assert d["sales_today_count"] == 1
    assert d["sales_today_revenue"] == 10.0
    assert d["revenue_30d"] == 15.0
    assert d["profit_30d"] == 9.0
    assert len(d["trend"]) == 30
    assert sum(p["revenue"] for p in d["trend"]) == 15.0
    assert d["trend"][-1]["revenue"] == 10.0
    assert [i["id"] for i in d["low_stock_items"]] == [1]
    assert d["low_stock_items"][0]["deficit"] == 4

    client.state["uid"] = 1  # user with no data
    d = client.get("/api/v1/dashboard/summary").json()
    assert d["total_products"] == 0 and d["revenue_30d"] == 0
    assert len(d["trend"]) == 30


def test_non_admin_forbidden(client):
    client.state["uid"] = 2
    assert client.get("/api/v1/admin/users").status_code == 403
    assert client.get("/api/v1/admin/stats").status_code == 403
    assert (
        client.put("/api/v1/admin/users/3", json={"is_admin": True}).status_code == 403
    )


def test_admin_list_search_update(client):
    r = client.get("/api/v1/admin/users", params={"page_size": 2})
    body = r.json()
    assert body["total"] == 3 and len(body["items"]) == 2 and body["page"] == 1
    assert "hashed_password" not in body["items"][0]
    r = client.get("/api/v1/admin/users", params={"q": "bob"})
    assert [u["id"] for u in r.json()["items"]] == [2]

    r = client.put("/api/v1/admin/users/2", json={"is_active": False, "is_admin": True})
    assert r.status_code == 200
    assert r.json()["is_active"] is False and r.json()["is_admin"] is True
    assert client.put("/api/v1/admin/users/99", json={}).status_code == 404


def test_admin_cannot_self_demote_or_deactivate(client):
    r = client.put("/api/v1/admin/users/1", json={"is_admin": False})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "CONFLICT"
    r = client.put("/api/v1/admin/users/1", json={"is_active": False})
    assert r.status_code == 409
    assert (
        client.put("/api/v1/admin/users/1", json={"is_active": True}).status_code == 200
    )


def test_admin_stats(client, db):
    db.add(User(id=4, email="off@x.com", hashed_password="x", is_active=False))
    db.add_all([_product(2, 1, "A", 1, 1), _product(3, 2, "B", 1, 1)])
    db.flush()
    _sale(db, 2, 1, datetime.now(UTC), 1, 2)
    _sale(db, 3, 2, datetime.now(UTC) - timedelta(days=90), 2, 1)
    db.commit()
    assert client.get("/api/v1/admin/stats").json() == {
        "total_users": 4,
        "active_users": 3,
        "total_products": 2,
        "total_sales": 2,
        "total_revenue": 15.0,
    }
