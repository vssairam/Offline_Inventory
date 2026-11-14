"""Sales endpoints."""

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.sale import SaleCreate, SaleList, SaleRead
from app.services import sale_service

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("", response_model=SaleRead, status_code=201)
def create_sale(
    data: SaleCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return sale_service.create_sale(db, user.id, data, background_tasks)


@router.get("", response_model=SaleList)
def list_sales(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return sale_service.list_sales(db, user.id, date_from, date_to, page, page_size)


@router.get("/{sale_id}", response_model=SaleRead)
def get_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return sale_service.get_sale(db, user.id, sale_id)
