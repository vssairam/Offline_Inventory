"""FastAPI application entrypoint."""

import logging
import os

from fastapi import APIRouter, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.exceptions import AppException
from app.limiter import limiter
from app.routers import admin as admin_router
from app.routers import alerts as alerts_router
from app.routers import auth as auth_router
from app.routers import categories as categories_router
from app.routers import dashboard as dashboard_router
from app.routers import products as products_router
from app.routers import reports as reports_router
from app.routers import sales as sales_router
from app.routers import stock as stock_router

logger = logging.getLogger(__name__)


app = FastAPI(title=settings.APP_NAME, version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _error(
    status_code: int, code: str, message: str, details: object = None
) -> JSONResponse:
    body: dict[str, object] = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details  # type: ignore[index]
    return JSONResponse(status_code=status_code, content=body)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return _error(exc.status_code, exc.code, exc.message)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return _error(exc.status_code, "HTTP_ERROR", str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return _error(
        422,
        "VALIDATION_ERROR",
        "Request validation failed",
        jsonable_encoder(exc.errors(), custom_encoder={Exception: str}),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error", exc_info=exc)
    return _error(500, "INTERNAL_ERROR", "Internal server error")


# All feature routers are mounted here under /api/v1 in Phase 2, e.g.:
#   api_router.include_router(auth.router)
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router.router)
api_router.include_router(sales_router.router)
api_router.include_router(stock_router.router)
api_router.include_router(alerts_router.router)
api_router.include_router(reports_router.router)
api_router.include_router(products_router.router)
api_router.include_router(categories_router.router)
api_router.include_router(dashboard_router.router)
api_router.include_router(admin_router.router)
app.include_router(api_router)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
