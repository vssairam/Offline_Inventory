"""Auth endpoint tests."""

from app.auth.jwt import create_refresh_token

A = "/api/v1/auth"


def _register(client, email="new@x.com", password="password123", **kw):
    return client.post(
        f"{A}/register", json={"email": email, "password": password, **kw}
    )


def _login(client, email, password):
    return client.post(f"{A}/login", json={"email": email, "password": password})


def test_register_ok_and_email_lowercased(client):
    r = _register(client, email="New@X.com", full_name="N")
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["email"] == "new@x.com"
    assert body["user"]["is_admin"] is False
    assert body["access_token"] and body["refresh_token"]
    assert "hashed_password" not in body["user"]


def test_register_duplicate_and_validation(client):
    assert _register(client).status_code == 201
    dup = _register(client, email="NEW@x.com")
    assert dup.status_code == 409 and dup.json()["error"]["code"] == "CONFLICT"
    assert _register(client, email="b@x.com", password="short").status_code == 422
    assert _register(client, email="not-an-email").status_code == 422


def test_login_ok_and_failures(client, make_user):
    make_user("a@x.com")
    ok = _login(client, "A@x.com", "password123")
    assert ok.status_code == 200 and ok.json()["access_token"]
    assert _login(client, "a@x.com", "wrongpass1").status_code == 401
    assert _login(client, "z@x.com", "x").status_code == 401


def test_login_disabled_account(client, make_user):
    make_user("off@x.com", is_active=False)
    r = _login(client, "off@x.com", "password123")
    assert r.status_code == 401 and "disabled" in r.json()["error"]["message"]


def test_me_requires_auth_and_returns_user(client, user1, h1):
    assert client.get(f"{A}/me").status_code == 401
    bad = client.get(f"{A}/me", headers={"Authorization": "Bearer junk"})
    assert bad.status_code == 401
    r = client.get(f"{A}/me", headers=h1)
    assert r.status_code == 200 and r.json()["email"] == "u1@x.com"


def test_access_token_rejected_for_inactive_user(client, db, user1, h1):
    user1.is_active = False
    db.commit()
    assert client.get(f"{A}/me", headers=h1).status_code == 401


def test_refresh_token_not_accepted_as_access(client, user1):
    token, _ = create_refresh_token(int(user1.id))
    r = client.get(f"{A}/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_refresh_rotation(client):
    old = _register(client).json()["refresh_token"]
    r = client.post(f"{A}/refresh", json={"refresh_token": old})
    assert r.status_code == 200
    new = r.json()
    assert new["refresh_token"] != old
    me = client.get(
        f"{A}/me", headers={"Authorization": f"Bearer {new['access_token']}"}
    )
    assert me.status_code == 200
    again = client.post(f"{A}/refresh", json={"refresh_token": new["refresh_token"]})
    assert again.status_code == 200  # a normal chain keeps working


def test_refresh_reuse_revokes_all_sessions(client):
    old = _register(client).json()["refresh_token"]
    new = client.post(f"{A}/refresh", json={"refresh_token": old}).json()
    # replaying the rotated token is treated as theft...
    assert client.post(f"{A}/refresh", json={"refresh_token": old}).status_code == 401
    # ...and also kills the legitimate descendant token
    assert (
        client.post(
            f"{A}/refresh", json={"refresh_token": new["refresh_token"]}
        ).status_code
        == 401
    )


def test_refresh_rejects_garbage_access_and_unknown(client, user1, h1):
    assert (
        client.post(f"{A}/refresh", json={"refresh_token": "junk"}).status_code == 401
    )
    access = h1["Authorization"].split()[1]
    assert (
        client.post(f"{A}/refresh", json={"refresh_token": access}).status_code == 401
    )
    unknown, _ = create_refresh_token(int(user1.id))  # signed but never stored
    assert (
        client.post(f"{A}/refresh", json={"refresh_token": unknown}).status_code == 401
    )


def test_logout_revokes_specific_and_all(client):
    t = _register(client).json()
    h = {"Authorization": f"Bearer {t['access_token']}"}
    second = _login(client, "new@x.com", "password123").json()
    out = client.post(
        f"{A}/logout", headers=h, json={"refresh_token": t["refresh_token"]}
    )
    assert out.status_code == 204
    revoked = client.post(f"{A}/refresh", json={"refresh_token": t["refresh_token"]})
    assert revoked.status_code == 401
    assert client.post(f"{A}/logout", headers=h).status_code == 204
    gone = client.post(f"{A}/refresh", json={"refresh_token": second["refresh_token"]})
    assert gone.status_code == 401
    assert client.post(f"{A}/logout").status_code == 401


def test_update_profile_name_and_password(client, h1):
    r = client.put(f"{A}/me", headers=h1, json={"full_name": "Zed"})
    assert r.status_code == 200 and r.json()["full_name"] == "Zed"

    wrong = client.put(
        f"{A}/me",
        headers=h1,
        json={"password": "newpassword1", "current_password": "nope"},
    )
    assert wrong.status_code == 422
    missing = client.put(f"{A}/me", headers=h1, json={"password": "newpassword1"})
    assert missing.status_code == 422

    ok = client.put(
        f"{A}/me",
        headers=h1,
        json={"password": "newpassword1", "current_password": "password123"},
    )
    assert ok.status_code == 200
    assert _login(client, "u1@x.com", "newpassword1").status_code == 200
    assert _login(client, "u1@x.com", "password123").status_code == 401


def test_health(client):
    assert client.get("/health").json() == {"status": "healthy"}


def test_unknown_route_uses_error_envelope(client):
    r = client.get("/api/v1/nope")
    assert r.status_code == 404 and r.json()["error"]["code"] == "HTTP_ERROR"
