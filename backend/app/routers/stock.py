"""Stock endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.stock import StockList
from app.services import stock_service

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("", response_model=StockList)
def list_stock(
    low_stock: bool = False,
    q: str | None = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return stock_service.list_stock(db, user.id, low_stock, q, page, page_size)
