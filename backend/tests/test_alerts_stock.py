"""Alert + stock tests (SQLite in-memory)."""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.dependencies import get_current_user, get_db
from app.main import app
from app.models.alert import Alert
from app.models.base import Base
from app.models.product import Product
from app.models.user import User
from app.schemas.sale import SaleCreate
from app.services import alert_service, email_service, sale_service


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    for i in (1, 2):
        session.add(User(id=i, email=f"u{i}@x.com", hashed_password="x"))

    def prod(pid, uid, name, qty, reorder):
        return Product(
            id=pid,
            user_id=uid,
            name=name,
            sku=f"S{pid}",
            price=Decimal(1),
            cost=Decimal(1),
            quantity=qty,
            reorder_level=reorder,
        )

    session.add_all(
        [
            prod(1, 1, "Widget", 10, 5),
            prod(2, 1, "Gadget", 100, 5),
            prod(3, 2, "Other", 10, 5),
        ]
    )
    session.commit()
    yield session
    session.close()


def _sell(db, uid, pid, qty):
    sale_service.create_sale(
        db, uid, SaleCreate(items=[{"product_id": pid, "quantity": qty}])
    )


def _alerts(db, uid):
    return db.execute(select(Alert).where(Alert.user_id == uid)).scalars().all()


def test_alert_created_on_crossing(db):
    _sell(db, 1, 1, 5)  # 10 -> 5 == reorder_level
    alerts = _alerts(db, 1)
    assert len(alerts) == 1
    assert alerts[0].type == "low_stock"
    assert alerts[0].product_id == 1
    assert not alerts[0].is_read


def test_alert_only_on_threshold_crossing(db):
    _sell(db, 1, 1, 6)  # crosses the threshold
    _sell(db, 1, 1, 1)  # still low, unread alert exists
    assert len(_alerts(db, 1)) == 1
    alert_service.mark_read(db, 1, _alerts(db, 1)[0].id)
    _sell(db, 1, 1, 1)  # still low, no new crossing -> no new alert
    assert len(_alerts(db, 1)) == 1
    # restock above the threshold, then cross again -> a new alert
    product = db.get(Product, 1)
    product.quantity = 50
    db.commit()
    _sell(db, 1, 1, 46)
    assert len(_alerts(db, 1)) == 2


def test_no_alert_above_threshold(db):
    _sell(db, 1, 2, 5)  # 95 left
    _sell(db, 1, 1, 4)  # 6 left > 5
    assert _alerts(db, 1) == []


def test_per_user_isolation(db):
    _sell(db, 2, 3, 6)
    assert len(_alerts(db, 2)) == 1
    assert _alerts(db, 1) == []
    result = alert_service.list_alerts(db, 1, False, 1, 20)
    assert result["total"] == 0 and result["unread_count"] == 0
    from app.exceptions import NotFoundError

    with pytest.raises(NotFoundError):
        alert_service.mark_read(db, 1, _alerts(db, 2)[0].id)


def test_email_failure_never_fails_sale(db, monkeypatch):
    monkeypatch.setattr(email_service.settings, "SMTP_HOST", "smtp.real.test")

    def boom(*a, **k):
        raise RuntimeError("smtp down")

    monkeypatch.setattr(email_service, "_send", boom)
    sale = sale_service.create_sale(
        db, 1, SaleCreate(items=[{"product_id": 1, "quantity": 6}])
    )
    assert sale.id
    email_service.send_alert_emails([a.id for a in _alerts(db, 1)], lambda: db)
    db.expire_all()
    assert _alerts(db, 1)[0].email_sent is False


def test_email_sent_flag(db, monkeypatch):
    monkeypatch.setattr(email_service.settings, "SMTP_HOST", "smtp.real.test")
    sent = []
    monkeypatch.setattr(email_service, "_send", lambda *a: sent.append(a))
    _sell(db, 1, 1, 6)
    email_service.send_alert_emails([a.id for a in _alerts(db, 1)], lambda: db)
    db.expire_all()
    assert sent and sent[0][0] == "u1@x.com"
    assert _alerts(db, 1)[0].email_sent is True


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: db.get(User, 1)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_stock_endpoint_filter(db, client):
    r = client.get("/api/v1/stock")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2 and {"items", "page", "page_size"} <= body.keys()
    assert all(i["is_low"] is False for i in body["items"])

    _sell(db, 1, 1, 6)
    low = client.get("/api/v1/stock", params={"low_stock": True}).json()
    assert low["total"] == 1
    item = low["items"][0]
    assert item["name"] == "Widget" and item["is_low"] is True
    assert set(item) == {"id", "name", "sku", "quantity", "reorder_level", "is_low"}
    assert client.get("/api/v1/stock", params={"q": "gad"}).json()["total"] == 1


def test_alerts_endpoints(db, client):
    _sell(db, 1, 1, 6)
    body = client.get("/api/v1/alerts", params={"unread_only": True}).json()
    assert body["total"] == 1 and body["unread_count"] == 1
    aid = body["items"][0]["id"]
    assert body["items"][0]["product_name"] == "Widget"
    r = client.put(f"/api/v1/alerts/{aid}/read")
    assert r.status_code == 200 and r.json()["is_read"] is True
    body = client.get("/api/v1/alerts", params={"unread_only": True}).json()
    assert body["total"] == 0 and body["unread_count"] == 0
    assert client.put("/api/v1/alerts/9999/read").status_code == 404
