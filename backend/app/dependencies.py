"""Shared FastAPI dependencies.

get_current_user / require_admin are stubs; implemented in Phase 2 (Auth module).
"""

from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import ForbiddenError, UnauthorizedError

__all__ = ["get_current_user", "get_db", "oauth2_scheme", "require_admin"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Any:
    """Decode the JWT access token and load the active User."""
    from app.auth.jwt import decode_token
    from app.models.user import User

    payload = decode_token(token, "access")
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Invalid token") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    return user


def require_admin(user: Any = Depends(get_current_user)) -> Any:
    """Ensure user.is_admin is True."""
    if not getattr(user, "is_admin", False):
        raise ForbiddenError("Admin access required")
    return user
