"""Product business logic. Every query is scoped by user_id."""

import secrets
from decimal import Decimal
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.exceptions import ConflictError, FileUploadError, NotFoundError
from app.models.category import Category
from app.models.product import Product
from app.models.sale import SaleItem
from app.schemas.product import ProductCreate, ProductUpdate

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _money(value: float) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _sku_exists(db: Session, user_id: int, sku: str, exclude_id: int | None) -> bool:
    q = db.query(Product.id).filter(Product.user_id == user_id, Product.sku == sku)
    if exclude_id is not None:
        q = q.filter(Product.id != exclude_id)
    return q.first() is not None


def _check_category(db: Session, user_id: int, category_id: int | None) -> None:
    if category_id is None:
        return
    found = (
        db.query(Category.id)
        .filter(Category.id == category_id, Category.user_id == user_id)
        .first()
    )
    if found is None:
        raise NotFoundError("Category")


def list_products(
    db: Session,
    user_id: int,
    q: str | None = None,
    category_id: int | None = None,
    low_stock: bool = False,
    include_inactive: bool = False,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Product], int]:
    query = db.query(Product).filter(Product.user_id == user_id)
    if not include_inactive:
        query = query.filter(Product.is_active.is_(True))
    if q and q.strip():
        term = q.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        like = f"%{term}%"
        query = query.filter(
            or_(
                Product.name.ilike(like, escape="\\"),
                Product.sku.ilike(like, escape="\\"),
            )
        )
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if low_stock:
        query = query.filter(Product.quantity <= Product.reorder_level)
    total = query.count()
    items = (
        query.order_by(Product.name, Product.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_product(db: Session, user_id: int, product_id: int) -> Product:
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.user_id == user_id)
        .first()
    )
    if product is None:
        raise NotFoundError("Product")
    return product


def create_product(db: Session, user_id: int, data: ProductCreate) -> Product:
    sku = data.sku.strip()
    if _sku_exists(db, user_id, sku, None):
        raise ConflictError("SKU already exists")
    _check_category(db, user_id, data.category_id)
    product = Product(
        user_id=user_id,
        category_id=data.category_id,
        name=data.name.strip(),
        sku=sku,
        price=_money(data.price),
        cost=_money(data.cost),
        quantity=data.quantity,
        reorder_level=data.reorder_level,
    )
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("SKU already exists") from None
    db.refresh(product)
    return product


def update_product(
    db: Session, user_id: int, product_id: int, data: ProductUpdate
) -> Product:
    product = get_product(db, user_id, product_id)
    sku = data.sku.strip()
    if _sku_exists(db, user_id, sku, product_id):
        raise ConflictError("SKU already exists")
    _check_category(db, user_id, data.category_id)
    product.name = data.name.strip()  # type: ignore[assignment]
    product.sku = sku  # type: ignore[assignment]
    product.price = _money(data.price)  # type: ignore[assignment]
    product.cost = _money(data.cost)  # type: ignore[assignment]
    product.quantity = data.quantity  # type: ignore[assignment]
    product.reorder_level = data.reorder_level  # type: ignore[assignment]
    product.category_id = data.category_id  # type: ignore[assignment]
    if data.is_active is not None:
        product.is_active = data.is_active  # type: ignore[assignment]
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("SKU already exists") from None
    db.refresh(product)
    return product


def delete_product(db: Session, user_id: int, product_id: int) -> bool:
    """Delete a product. Returns True if hard-deleted, False if deactivated.

    A product referenced by sale items cannot be removed (sales history must be
    preserved), so it is soft-deactivated (is_active=False) instead.
    """
    product = get_product(db, user_id, product_id)
    has_sales = (
        db.query(SaleItem.id).filter(SaleItem.product_id == product_id).first()
        is not None
    )
    if has_sales:
        product.is_active = False  # type: ignore[assignment]
        db.commit()
        return False
    image_url = product.image_url
    db.delete(product)
    db.commit()
    _remove_file(str(image_url) if image_url else None)
    return True


def _remove_file(image_url: str | None) -> None:
    if not image_url:
        return
    path = Path(settings.UPLOAD_DIR) / Path(image_url).name
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def _detect_image_type(head: bytes) -> str | None:
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    return None


async def save_product_image(
    db: Session, user_id: int, product_id: int, file: UploadFile
) -> Product:
    product = get_product(db, user_id, product_id)
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise FileUploadError("Only JPEG, PNG or WebP images are allowed")
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    data = await file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise FileUploadError(f"File exceeds {settings.MAX_UPLOAD_MB} MB limit")
    if not data:
        raise FileUploadError("Empty file")
    detected = _detect_image_type(data[:12])
    if detected is None:
        raise FileUploadError("File content is not a valid JPEG, PNG or WebP image")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{secrets.token_hex(16)}{ALLOWED_IMAGE_TYPES[detected]}"
    (upload_dir / filename).write_bytes(data)

    old = product.image_url
    product.image_url = f"/uploads/{filename}"  # type: ignore[assignment]
    db.commit()
    db.refresh(product)
    _remove_file(str(old) if old else None)
    return product
