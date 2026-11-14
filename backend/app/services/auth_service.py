"""Authentication business logic."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.exceptions import ConflictError, UnauthorizedError, ValidationFailedError
from app.models.user import RefreshToken, User
from app.schemas.auth import RegisterRequest, UserUpdate


def _issue_tokens(db: Session, user: User) -> dict[str, str]:
    refresh_token, expires_at = create_refresh_token(user.id)
    db.add(RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at))
    db.commit()
    return {
        "access_token": create_access_token(user.id),
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def register(db: Session, data: RegisterRequest) -> tuple[User, dict[str, str]]:
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise ConflictError("Email already registered")
    user = User(
        email=email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, _issue_tokens(db, user)


def login(db: Session, email: str, password: str) -> tuple[User, dict[str, str]]:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedError("Account is disabled")
    return user, _issue_tokens(db, user)


def refresh(db: Session, refresh_token: str) -> dict[str, str]:
    payload = decode_token(refresh_token, "refresh")
    stored = db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token == refresh_token)
        .with_for_update()
    )
    if not stored:
        raise UnauthorizedError("Refresh token revoked or unknown")
    if stored.revoked:
        # A rotated/revoked token is being replayed: treat as theft and end all sessions.
        revoke_all_refresh_tokens(db, stored.user_id)
        db.commit()
        raise UnauthorizedError("Refresh token revoked or unknown")
    expires = stored.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expires < datetime.now(UTC):
        raise UnauthorizedError("Refresh token expired")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    stored.revoked = True  # rotation: old token is single-use
    return _issue_tokens(db, user)


def revoke_all_refresh_tokens(db: Session, user_id: int) -> None:
    """Revoke every active refresh token of a user (does not commit)."""
    for token in db.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False)
        )
    ):
        token.revoked = True


def logout(db: Session, user: User, refresh_token: str | None = None) -> None:
    query = select(RefreshToken).where(
        RefreshToken.user_id == user.id, RefreshToken.revoked.is_(False)
    )
    if refresh_token:
        query = query.where(RefreshToken.token == refresh_token)
    for token in db.scalars(query):
        token.revoked = True
    db.commit()


def update_profile(db: Session, user: User, data: UserUpdate) -> User:
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.password:
        if not data.current_password or not verify_password(
            data.current_password, user.hashed_password
        ):
            raise ValidationFailedError("Current password is incorrect")
        user.hashed_password = hash_password(data.password)
        revoke_all_refresh_tokens(db, user.id)  # password change ends other sessions
    db.commit()
    db.refresh(user)
    return user
