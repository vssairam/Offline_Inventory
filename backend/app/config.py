"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Inventory Management"
    ENVIRONMENT: str = "development"  # anything else enforces production safety checks
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/inventory_management"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SMTP_HOST: str = "smtp.example.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "alerts@example.com"

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 5

    VITE_API_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    RATE_LIMIT_DEFAULT: str = "100/minute"

    @model_validator(mode="after")
    def _require_strong_secret_outside_dev(self) -> "Settings":
        weak = (
            self.SECRET_KEY in {"your-secret-key", "change-me", ""}
            or len(self.SECRET_KEY) < 32
        )
        if self.ENVIRONMENT != "development" and weak:
            raise ValueError(
                "SECRET_KEY must be set to a random value of at least 32 characters "
                "(generate one with: openssl rand -hex 32)"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
