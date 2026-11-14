from typing import Any

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db), user: Any = Depends(get_current_user)
) -> Any:
    return category_service.list_categories(db, user.id)


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user),
) -> Any:
    return category_service.create_category(db, user.id, data)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user),
) -> Any:
    return category_service.update_category(db, user.id, category_id, data)


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user: Any = Depends(get_current_user),
) -> Response:
    category_service.delete_category(db, user.id, category_id)
    return Response(status_code=204)
