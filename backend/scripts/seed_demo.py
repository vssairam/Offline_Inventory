"""Seed demo data into a RUNNING Inventory Management API.

Registers a demo account, then creates categories, products and sales through the
public API, so the data goes through the same validation, stock deduction and
low-stock alert logic as normal use. Safe to re-run: existing data is detected and
the script stops instead of duplicating it.

Usage (from backend/):
    python scripts/seed_demo.py
    API_URL=http://localhost:8001/api/v1 python scripts/seed_demo.py

Demo login: demo@example.com / demo12345 (local development only).
Make the demo user an admin:  python scripts/make_admin.py demo@example.com
"""

import json
import os
import random
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta

B = os.environ.get("API_URL", "http://localhost:8000/api/v1")
EMAIL, PASSWORD = "demo@example.com", "demo12345"


def call(method, path, body=None, token=None):
    req = urllib.request.Request(
        B + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"null")


s, d = call(
    "POST",
    "/auth/register",
    {"email": EMAIL, "password": PASSWORD, "full_name": "Demo Owner"},
)
if s == 409:
    s, d = call("POST", "/auth/login", {"email": EMAIL, "password": PASSWORD})
assert s in (200, 201), (s, d)
tok = d["access_token"]
print("account:", EMAIL, "->", s)

cats = {}
for name in ["Beverages", "Snacks", "Stationery", "Household"]:
    s, d = call("POST", "/categories", {"name": name}, tok)
    if s != 409:
        cats[name] = d["id"]
if not cats:
    _, lst = call("GET", "/categories", token=tok)
    cats = {c["name"]: c["id"] for c in lst}
print("categories:", len(cats))

# name, sku, category, price, cost, quantity, reorder_level
products = [
    ("Mineral Water 1L", "BEV-001", "Beverages", 1.20, 0.60, 120, 30),
    ("Orange Juice 1L", "BEV-002", "Beverages", 3.50, 2.10, 60, 20),
    ("Cola 330ml", "BEV-003", "Beverages", 1.50, 0.80, 90, 25),
    ("Green Tea Box", "BEV-004", "Beverages", 4.80, 3.00, 25, 10),
    ("Potato Chips", "SNK-001", "Snacks", 2.20, 1.20, 80, 20),
    ("Chocolate Bar", "SNK-002", "Snacks", 1.80, 0.90, 70, 20),
    ("Salted Peanuts", "SNK-003", "Snacks", 2.90, 1.70, 30, 12),
    ("Oat Cookies", "SNK-004", "Snacks", 3.20, 1.90, 18, 10),
    ("Ballpoint Pen (Blue)", "STA-001", "Stationery", 0.90, 0.35, 200, 50),
    ("A4 Notebook", "STA-002", "Stationery", 2.75, 1.40, 45, 15),
    ("Sticky Notes", "STA-003", "Stationery", 1.95, 0.95, 22, 12),
    ("Stapler", "STA-004", "Stationery", 6.50, 3.80, 12, 5),
    ("Dish Soap 500ml", "HOU-001", "Household", 3.10, 1.80, 40, 12),
    ("Paper Towels 2-pack", "HOU-002", "Household", 4.25, 2.60, 35, 10),
    ("LED Bulb 9W", "HOU-003", "Household", 3.75, 2.20, 15, 8),
    ("Trash Bags 30ct", "HOU-004", "Household", 5.40, 3.10, 9, 8),
]
ids = {}
for name, sku, cat, price, cost, qty, reorder in products:
    s, d = call(
        "POST",
        "/products",
        {
            "name": name,
            "sku": sku,
            "category_id": cats[cat],
            "price": price,
            "cost": cost,
            "quantity": qty,
            "reorder_level": reorder,
        },
        tok,
    )
    if s == 201:
        ids[sku] = d["id"]
    elif s == 409:
        print("exists:", sku)
print("products created:", len(ids))
if not ids:
    raise SystemExit("nothing new to seed (already seeded)")

random.seed(7)
now = datetime.now(UTC)
ok = fail = 0
skus = list(ids)
for day in range(14, -1, -1):
    for _ in range(random.randint(1, 3)):
        lines = []
        for sku in random.sample(skus, random.randint(1, 4)):
            lines.append({"product_id": ids[sku], "quantity": random.randint(1, 6)})
        when = (now - timedelta(days=day, hours=random.randint(0, 8))).isoformat()
        s, d = call("POST", "/sales", {"items": lines, "sold_at": when}, tok)
        ok, fail = (ok + 1, fail) if s == 201 else (ok, fail + 1)
# push a few items below their reorder level so alerts/low-stock views have data
for sku, qty in [("HOU-004", 3), ("STA-004", 6), ("SNK-004", 12)]:
    if sku in ids:
        s, d = call(
            "POST",
            "/sales",
            {"items": [{"product_id": ids[sku], "quantity": qty}]},
            tok,
        )
        ok, fail = (ok + 1, fail) if s == 201 else (ok, fail + 1)
print(f"sales recorded: {ok}, failed: {fail}")

_, rep = call("GET", "/reports/sales", token=tok)
_, dash = call("GET", "/dashboard/summary", token=tok)
_, al = call("GET", "/alerts", token=tok)
print(
    "report:",
    rep["total_sales_count"],
    "sales | revenue",
    rep["total_revenue"],
    "| profit",
    rep["total_profit"],
)
print(
    "dashboard: products",
    dash["total_products"],
    "| low stock",
    dash["low_stock_count"],
    "| stock value",
    dash["total_stock_value"],
)
print("alerts:", al["total"], "| unread", al["unread_count"])
for a in al["items"][:6]:
    print("  -", a["message"])
