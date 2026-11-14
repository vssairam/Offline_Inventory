"""Product + category API tests, including per-user isolation and uploads."""

import os

from app.config import settings

P = "/api/v1/products"
C = "/api/v1/categories"

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32
JPG = b"\xff\xd8\xff\xe0" + b"0" * 32
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"0" * 32


def _body(sku="S1", **kw):
    return {
        "name": "Widget",
        "sku": sku,
        "price": 10.5,
        "cost": 4,
        "quantity": 10,
        "reorder_level": 2,
        **kw,
    }


def _create(client, h, **kw):
    r = client.post(P, json=_body(**kw), headers=h)
    assert r.status_code == 201, r.text
    return r.json()


def _upload(client, h, pid, data, ctype="image/png"):
    return client.post(
        f"{P}/{pid}/image", headers=h, files={"file": ("f", data, ctype)}
    )


def test_requires_auth(client):
    assert client.get(P).status_code == 401
    assert client.post(P, json=_body()).status_code == 401
    assert client.get(C).status_code == 401


def test_product_crud(client, h1):
    p = _create(client, h1, sku=" S1 ")
    assert p["sku"] == "S1" and p["price"] == 10.5 and p["is_active"] is True
    assert client.get(f"{P}/{p['id']}", headers=h1).json()["name"] == "Widget"

    upd = client.put(
        f"{P}/{p['id']}", headers=h1, json=_body(sku="S1", name="Renamed", quantity=3)
    )
    assert upd.status_code == 200
    assert upd.json()["name"] == "Renamed" and upd.json()["quantity"] == 3

    d = client.delete(f"{P}/{p['id']}", headers=h1)
    assert d.json() == {"id": p["id"], "deleted": True, "deactivated": False}
    assert client.get(f"{P}/{p['id']}", headers=h1).status_code == 404


def test_product_validation(client, h1):
    assert client.post(P, headers=h1, json=_body(price=-1)).status_code == 422
    assert client.post(P, headers=h1, json=_body(name="")).status_code == 422
    assert client.post(P, headers=h1, json=_body(quantity=-1)).status_code == 422
    assert client.get(f"{P}/9999", headers=h1).status_code == 404


def test_sku_conflict_create_and_update(client, h1, h2):
    a = _create(client, h1, sku="A")
    b = _create(client, h1, sku="B")
    assert client.post(P, headers=h1, json=_body(sku="A")).status_code == 409
    clash = client.put(f"{P}/{b['id']}", headers=h1, json=_body(sku="A"))
    assert clash.status_code == 409
    same = client.put(f"{P}/{a['id']}", headers=h1, json=_body(sku="A"))
    assert same.status_code == 200
    assert client.post(P, headers=h2, json=_body(sku="A")).status_code == 201


def test_list_search_filter_pagination(client, h1):
    cat = client.post(C, headers=h1, json={"name": "Tools"}).json()
    _create(
        client,
        h1,
        sku="HAM-1",
        name="Hammer",
        category_id=cat["id"],
        quantity=1,
        reorder_level=5,
    )
    _create(client, h1, sku="SAW-1", name="Saw", quantity=50, reorder_level=5)
    _create(client, h1, sku="PCT_1", name="100% Pure", quantity=50)
    off = _create(client, h1, sku="OFF", name="Zzz")
    client.put(
        f"{P}/{off['id']}",
        headers=h1,
        json=_body(sku="OFF", name="Zzz", is_active=False),
    )

    def names(**params):
        r = client.get(P, headers=h1, params=params)
        assert r.status_code == 200
        return [i["name"] for i in r.json()["items"]]

    assert names() == ["100% Pure", "Hammer", "Saw"]  # inactive hidden
    assert "Zzz" in names(include_inactive=True)
    assert names(q="ham") == ["Hammer"]
    assert names(q="saw-1") == ["Saw"]  # matches sku
    assert names(q="%") == ["100% Pure"]  # wildcard escaped
    assert names(q="_") == ["100% Pure"]
    assert names(category_id=cat["id"]) == ["Hammer"]
    assert names(low_stock=True) == ["Hammer"]
    page = client.get(P, headers=h1, params={"page": 2, "page_size": 2}).json()
    assert page["total"] == 3 and len(page["items"]) == 1
    assert client.get(P, headers=h1, params={"page_size": 101}).status_code == 422


def test_delete_with_sales_deactivates(client, h1):
    p = _create(client, h1)
    sale = client.post(
        "/api/v1/sales",
        headers=h1,
        json={"items": [{"product_id": p["id"], "quantity": 1}]},
    )
    assert sale.status_code == 201
    d = client.delete(f"{P}/{p['id']}", headers=h1).json()
    assert d["deleted"] is False and d["deactivated"] is True
    assert client.get(f"{P}/{p['id']}", headers=h1).json()["is_active"] is False


def test_product_isolation(client, h1, h2):
    pid = _create(client, h1)["id"]
    assert client.get(f"{P}/{pid}", headers=h2).status_code == 404
    assert client.put(f"{P}/{pid}", headers=h2, json=_body(sku="Q")).status_code == 404
    assert client.delete(f"{P}/{pid}", headers=h2).status_code == 404
    assert _upload(client, h2, pid, PNG).status_code == 404
    assert client.get(P, headers=h2).json()["total"] == 0
    cat = client.post(C, headers=h1, json={"name": "Mine"}).json()
    steal = client.post(P, headers=h2, json=_body(sku="Z", category_id=cat["id"]))
    assert steal.status_code == 404
    assert client.get(f"{P}/{pid}", headers=h1).status_code == 200


def test_product_update_bad_category(client, h1):
    p = _create(client, h1)
    r = client.put(f"{P}/{p['id']}", headers=h1, json=_body(category_id=999))
    assert r.status_code == 404


def test_image_upload_ok_replace_and_delete(client, h1, uploads):
    pid = _create(client, h1)["id"]
    r = _upload(client, h1, pid, PNG)
    assert r.status_code == 200
    url = r.json()["image_url"]
    assert url.startswith("/uploads/") and url.endswith(".png")
    assert (uploads / os.path.basename(url)).exists()

    r2 = _upload(client, h1, pid, JPG, "image/jpeg")
    url2 = r2.json()["image_url"]
    assert url2.endswith(".jpg") and url2 != url
    assert not (uploads / os.path.basename(url)).exists()  # old file removed

    r3 = _upload(client, h1, pid, WEBP, "image/webp")
    assert r3.json()["image_url"].endswith(".webp")

    client.delete(f"{P}/{pid}", headers=h1)
    assert list(uploads.iterdir()) == []  # file removed with product


def test_image_upload_rejections(client, h1, monkeypatch):
    pid = _create(client, h1)["id"]

    bad_type = _upload(client, h1, pid, b"hello", "text/plain")
    assert bad_type.status_code == 400
    assert bad_type.json()["error"]["code"] == "FILE_UPLOAD_ERROR"
    assert (
        _upload(client, h1, pid, b"GIF89a" + b"0" * 20, "image/gif").status_code == 400
    )
    # magic-bytes mismatch: claims PNG but content is not an image
    assert _upload(client, h1, pid, b"<html>not an image</html>").status_code == 400
    assert _upload(client, h1, pid, b"").status_code == 400  # empty
    monkeypatch.setattr(settings, "MAX_UPLOAD_MB", 1)
    over = _upload(client, h1, pid, PNG + b"0" * (1024 * 1024))
    assert over.status_code == 400 and "limit" in over.json()["error"]["message"]
    assert client.get(f"{P}/{pid}", headers=h1).json()["image_url"] is None


def test_image_detected_type_wins_over_declared(client, h1):
    pid = _create(client, h1)["id"]
    r = _upload(client, h1, pid, JPG, "image/png")
    assert r.status_code == 200 and r.json()["image_url"].endswith(".jpg")


def test_category_crud_conflict_isolation(client, h1, h2):
    a = client.post(C, headers=h1, json={"name": "  Tools "})
    assert a.status_code == 201 and a.json()["name"] == "Tools"
    cid = a.json()["id"]
    assert client.post(C, headers=h1, json={"name": "Tools"}).status_code == 409
    assert client.post(C, headers=h1, json={"name": "   "}).status_code == 422
    assert client.post(C, headers=h2, json={"name": "Tools"}).status_code == 201

    b = client.post(C, headers=h1, json={"name": "Parts"}).json()
    assert [c["name"] for c in client.get(C, headers=h1).json()] == ["Parts", "Tools"]
    clash = client.put(f"{C}/{b['id']}", headers=h1, json={"name": "Tools"})
    assert clash.status_code == 409
    same = client.put(f"{C}/{b['id']}", headers=h1, json={"name": "Parts"})
    assert same.status_code == 200
    renamed = client.put(f"{C}/{b['id']}", headers=h1, json={"name": "Bits"})
    assert renamed.json()["name"] == "Bits"

    assert client.put(f"{C}/{cid}", headers=h2, json={"name": "X"}).status_code == 404
    assert client.delete(f"{C}/{cid}", headers=h2).status_code == 404
    assert len(client.get(C, headers=h2).json()) == 1


def test_category_delete_keeps_products(client, h1):
    cat = client.post(C, headers=h1, json={"name": "Tools"}).json()
    p = _create(client, h1, category_id=cat["id"])
    assert client.delete(f"{C}/{cat['id']}", headers=h1).status_code == 204
    assert client.get(C, headers=h1).json() == []
    assert client.get(f"{P}/{p['id']}", headers=h1).status_code == 200
