"""Auth request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    current_password: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str | None = None
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(TokenResponse):
    user: UserResponse
