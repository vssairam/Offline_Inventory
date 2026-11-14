"""Sales and report endpoint tests with real auth and per-user isolation."""

from datetime import UTC, datetime, timedelta

S = "/api/v1/sales"
R = "/api/v1/reports"
PR = "/api/v1/products"


def _product(client, h, sku="S1", qty=10, price=10.0, cost=4.0, **kw):
    r = client.post(
        PR,
        headers=h,
        json={
            "name": f"P-{sku}",
            "sku": sku,
            "price": price,
            "cost": cost,
            "quantity": qty,
            "reorder_level": 0,
            **kw,
        },
    )
    assert r.status_code == 201, r.text
    return r.json()


def _sell(client, h, items, **kw):
    return client.post(
        S,
        headers=h,
        json={"items": [{"product_id": p, "quantity": q} for p, q in items], **kw},
    )


def test_sale_flow_and_stock(client, h1):
    p = _product(client, h1)
    r = _sell(client, h1, [(p["id"], 3)])
    assert r.status_code == 201
    sale = r.json()
    assert sale["total_amount"] == 30.0 and sale["item_count"] == 3
    assert client.get(f"{PR}/{p['id']}", headers=h1).json()["quantity"] == 7
    assert client.get(f"{S}/{sale['id']}", headers=h1).json()["id"] == sale["id"]
    lst = client.get(S, headers=h1).json()
    assert lst["total"] == 1 and lst["items"][0]["id"] == sale["id"]


def test_sale_errors(client, h1, h2):
    p = _product(client, h1, qty=2)
    assert _sell(client, h1, [(p["id"], 5)]).status_code == 409
    assert _sell(client, h1, [(9999, 1)]).status_code == 404
    assert _sell(client, h1, [(p["id"], 0)]).status_code == 422
    assert client.post(S, headers=h1, json={"items": []}).status_code == 422
    assert _sell(client, h2, [(p["id"], 1)]).status_code == 404
    assert client.get(f"{PR}/{p['id']}", headers=h1).json()["quantity"] == 2
    assert client.post(S, json={"items": []}).status_code == 401


def test_sale_inactive_product(client, h1):
    p = _product(client, h1)
    client.put(
        f"{PR}/{p['id']}",
        headers=h1,
        json={"name": "n", "sku": "S1", "price": 1, "cost": 1, "is_active": False},
    )
    r = _sell(client, h1, [(p["id"], 1)])
    assert r.status_code == 422 and "inactive" in r.json()["error"]["message"]


def test_sale_isolation_and_list_filters(client, h1, h2):
    p = _product(client, h1)
    now = datetime.now(UTC)
    old_at = (now - timedelta(days=10)).isoformat()
    old = _sell(client, h1, [(p["id"], 1)], sold_at=old_at).json()
    new = _sell(client, h1, [(p["id"], 1)]).json()
    assert client.get(f"{S}/{new['id']}", headers=h2).status_code == 404
    assert client.get(S, headers=h2).json()["total"] == 0

    cutoff = (now - timedelta(days=5)).isoformat()
    recent = client.get(S, headers=h1, params={"date_from": cutoff}).json()
    assert [s["id"] for s in recent["items"]] == [new["id"]]
    older = client.get(S, headers=h1, params={"date_to": cutoff}).json()
    assert [s["id"] for s in older["items"]] == [old["id"]]
    assert client.get(S, headers=h1, params={"page_size": 0}).status_code == 422


def test_low_stock_sale_creates_alert(client, h1):
    p = _product(client, h1, qty=5, reorder_level=3)
    assert _sell(client, h1, [(p["id"], 4)]).status_code == 201
    alerts = client.get("/api/v1/alerts", headers=h1)
    assert alerts.status_code == 200


def test_reports_empty_and_data(client, h1, h2):
    empty = client.get(f"{R}/sales", headers=h1).json()
    assert empty["total_sales_count"] == 0 and empty["total_revenue"] == 0
    assert empty["top_products"] == [] and empty["daily"] == []

    p = _product(client, h1, price=10, cost=4)
    _sell(client, h1, [(p["id"], 2)])
    rep = client.get(f"{R}/sales", headers=h1).json()
    assert rep["total_sales_count"] == 1
    assert rep["total_revenue"] == 20.0 and rep["total_cost"] == 8.0
    assert rep["total_profit"] == 12.0
    assert rep["top_products"][0]["quantity"] == 2

    assert client.get(f"{R}/sales", headers=h2).json()["total_sales_count"] == 0

    future = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    none = client.get(f"{R}/sales", headers=h1, params={"date_from": future}).json()
    assert none["total_sales_count"] == 0
    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    none2 = client.get(f"{R}/sales", headers=h1, params={"date_to": past}).json()
    assert none2["total_sales_count"] == 0
    assert client.get(f"{R}/sales").status_code == 401


def test_csv_export(client, h1, h2):
    p = _product(client, h1)
    _sell(client, h1, [(p["id"], 1)])
    r = client.get(f"{R}/sales/export", headers=h1)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    assert "sales.csv" in r.headers["content-disposition"]
    assert "P-S1" in r.text
    assert "P-S1" not in client.get(f"{R}/sales/export", headers=h2).text
    assert client.get(f"{R}/sales/export").status_code == 401
