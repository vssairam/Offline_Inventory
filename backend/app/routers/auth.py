"""Auth endpoints."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.limiter import limiter
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserUpdate,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(user: User, tokens: dict[str, str]) -> AuthResponse:
    return AuthResponse(**tokens, user=UserResponse.model_validate(user))


@router.post("/register", response_model=AuthResponse, status_code=201)
@limiter.limit("10/minute")
def register(
    request: Request, data: RegisterRequest, db: Session = Depends(get_db)
) -> AuthResponse:
    return _auth_response(*auth_service.register(db, data))


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
def login(
    request: Request, data: LoginRequest, db: Session = Depends(get_db)
) -> AuthResponse:
    return _auth_response(*auth_service.login(db, data.email, data.password))


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("20/minute")
def refresh(
    request: Request, data: RefreshRequest, db: Session = Depends(get_db)
) -> TokenResponse:
    return TokenResponse(**auth_service.refresh(db, data.refresh_token))


@router.post("/logout", status_code=204)
def logout(
    data: LogoutRequest | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    auth_service.logout(db, user, data.refresh_token if data else None)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.put("/me", response_model=UserResponse)
def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    return auth_service.update_profile(db, user, data)
