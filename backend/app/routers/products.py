from typing import Any

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.product import (
    ProductCreate,
    ProductDeleteResponse,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductListResponse)
def list_products(
    q: str | None = Query(None, max_length=100),
    category_id: int | None = None,
    low_stock: bool = False,
    include_inactive: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user),
) -> Any:
    items, total = product_service.list_products(
        db, user.id, q, category_id, low_stock, include_inactive, page, page_size
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user),
) -> Any:
    return product_service.create_product(db, user.id, data)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user),
) -> Any:
    return product_service.get_product(db, user.id, product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user),
) -> Any:
    return product_service.update_product(db, user.id, product_id, data)


@router.delete("/{product_id}", response_model=ProductDeleteResponse)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user),
) -> Any:
    deleted = product_service.delete_product(db, user.id, product_id)
    return {"id": product_id, "deleted": deleted, "deactivated": not deleted}


@router.post("/{product_id}/image", response_model=ProductResponse)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user),
) -> Any:
    return await product_service.save_product_image(db, user.id, product_id, file)
