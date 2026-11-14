"""Shared fixtures: SQLite in-memory DB, real-auth TestClient, user factory.

Modules with their own ``db``/``client`` fixtures keep working (local wins).
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.auth.jwt import create_access_token, hash_password
from app.config import settings
from app.database import get_db
from app.limiter import limiter
from app.main import app
from app.models.base import Base
from app.models.user import User


@pytest.fixture(autouse=True)
def _reset_limiter():
    limiter.reset()
    yield


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def uploads(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture
def client(db, uploads):
    def _db():
        yield db

    app.dependency_overrides[get_db] = _db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(db):
    def _make(email="u@x.com", password="password123", **kw) -> User:
        user = User(email=email, hashed_password=hash_password(password), **kw)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return _make


def headers_for(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(int(user.id))}"}


@pytest.fixture
def user1(make_user):
    return make_user("u1@x.com")


@pytest.fixture
def user2(make_user):
    return make_user("u2@x.com")


@pytest.fixture
def h1(user1):
    return headers_for(user1)


@pytest.fixture
def h2(user2):
    return headers_for(user2)
