"""Regression tests for review findings (secret key, sessions, validation, export)."""

import pytest
from pydantic import ValidationError

from app.config import Settings
from app.models.user import RefreshToken
from app.services import report_service

A = "/api/v1/auth"


def test_weak_secret_rejected_outside_development():
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="production", SECRET_KEY="your-secret-key")
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="production", SECRET_KEY="short")
    assert (
        Settings(ENVIRONMENT="production", SECRET_KEY="a" * 32).ENVIRONMENT
        == "production"
    )
    Settings(
        ENVIRONMENT="development", SECRET_KEY="your-secret-key"
    )  # dev may use default


def test_password_change_revokes_refresh_tokens(client, db):
    reg = client.post(
        f"{A}/register", json={"email": "p@x.com", "password": "password123"}
    )
    tokens = reg.json()
    h = {"Authorization": f"Bearer {tokens['access_token']}"}
    r = client.put(
        f"{A}/me",
        json={"password": "newpassword456", "current_password": "password123"},
        headers=h,
    )
    assert r.status_code == 200
    assert (
        client.post(
            f"{A}/refresh", json={"refresh_token": tokens["refresh_token"]}
        ).status_code
        == 401
    )


def test_admin_deactivation_revokes_refresh_tokens(client, db, make_user):
    from tests.conftest import headers_for

    admin = make_user("admin@x.com", is_admin=True)
    victim = client.post(
        f"{A}/register", json={"email": "v@x.com", "password": "password123"}
    ).json()
    vid = victim["user"]["id"]
    r = client.put(
        f"/api/v1/admin/users/{vid}",
        json={"is_active": False},
        headers=headers_for(admin),
    )
    assert r.status_code == 200
    assert all(
        t.revoked for t in db.query(RefreshToken).filter(RefreshToken.user_id == vid)
    )


def _product(client, h, **over):
    body = {
        "name": "Pen",
        "sku": "P1",
        "price": 1,
        "cost": 1,
        "quantity": 1,
        "reorder_level": 0,
    }
    body.update(over)
    return client.post("/api/v1/products", json=body, headers=h)


def test_quantity_upper_bound_and_whitespace_validation(client, h1):
    assert _product(client, h1, quantity=2_000_000_000).status_code == 422
    assert _product(client, h1, sku="   ").status_code == 422
    assert _product(client, h1, name="  ").status_code == 422
    ok = _product(client, h1, name="  Pen  ", sku=" X1 ")
    assert (
        ok.status_code == 201
        and ok.json()["sku"] == "X1"
        and ok.json()["name"] == "Pen"
    )


def test_product_put_without_is_active_keeps_it_inactive(client, h1):
    pid = _product(client, h1).json()["id"]
    body = {
        "name": "Pen",
        "sku": "P1",
        "price": 1,
        "cost": 1,
        "quantity": 1,
        "reorder_level": 0,
    }
    assert (
        client.put(
            f"/api/v1/products/{pid}", json={**body, "is_active": False}, headers=h1
        ).json()["is_active"]
        is False
    )
    assert (
        client.put(f"/api/v1/products/{pid}", json=body, headers=h1).json()["is_active"]
        is False
    )


def test_csv_export_row_cap(client, h1, db, monkeypatch):
    pid = _product(client, h1, quantity=100).json()["id"]
    for _ in range(3):
        client.post(
            "/api/v1/sales",
            json={"items": [{"product_id": pid, "quantity": 1}]},
            headers=h1,
        )
    assert client.get("/api/v1/reports/sales/export", headers=h1).status_code == 200
    monkeypatch.setattr(report_service, "MAX_EXPORT_ROWS", 2)
    r = client.get("/api/v1/reports/sales/export", headers=h1)
    assert r.status_code == 422
