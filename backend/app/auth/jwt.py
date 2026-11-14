"""Password hashing and JWT helpers."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import settings
from app.exceptions import UnauthorizedError


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode()[:72], hashed.encode())
    except ValueError:
        return False


def _create(subject: int, token_type: str, expires: timedelta) -> tuple[str, datetime]:
    expire = datetime.now(UTC) + expires
    payload = {
        "sub": str(subject),
        "type": token_type,
        "exp": expire,
        "jti": uuid.uuid4().hex,
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expire


def create_access_token(user_id: int) -> str:
    return _create(
        user_id, "access", timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )[0]


def create_refresh_token(user_id: int) -> tuple[str, datetime]:
    """Return (token, expires_at)."""
    return _create(
        user_id, "refresh", timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise UnauthorizedError("Invalid token type")
    return payload
