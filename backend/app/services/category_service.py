from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def _name_taken(db: Session, user_id: int, name: str, exclude_id: int | None) -> bool:
    q = db.query(Category.id).filter(Category.user_id == user_id, Category.name == name)
    if exclude_id is not None:
        q = q.filter(Category.id != exclude_id)
    return q.first() is not None


def list_categories(db: Session, user_id: int) -> list[Category]:
    return (
        db.query(Category)
        .filter(Category.user_id == user_id)
        .order_by(Category.name)
        .all()
    )


def get_category(db: Session, user_id: int, category_id: int) -> Category:
    cat = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user_id)
        .first()
    )
    if cat is None:
        raise NotFoundError("Category")
    return cat


def create_category(db: Session, user_id: int, data: CategoryCreate) -> Category:
    if _name_taken(db, user_id, data.name, None):
        raise ConflictError("Category name already exists")
    cat = Category(user_id=user_id, name=data.name)
    db.add(cat)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Category name already exists") from None
    db.refresh(cat)
    return cat


def update_category(
    db: Session, user_id: int, category_id: int, data: CategoryUpdate
) -> Category:
    cat = get_category(db, user_id, category_id)
    if _name_taken(db, user_id, data.name, category_id):
        raise ConflictError("Category name already exists")
    cat.name = data.name  # type: ignore[assignment]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("Category name already exists") from None
    db.refresh(cat)
    return cat


def delete_category(db: Session, user_id: int, category_id: int) -> None:
    """Products in the category keep existing (FK is ON DELETE SET NULL)."""
    cat = get_category(db, user_id, category_id)
    db.delete(cat)
    db.commit()
