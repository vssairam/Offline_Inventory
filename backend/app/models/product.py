from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name = Column(String(200), nullable=False)
    sku = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    cost = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=0)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="products")
    category = relationship("Category", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
    alerts = relationship(
        "Alert", back_populates="product", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "sku", name="uq_products_user_sku"),
        Index("ix_products_user_name", "user_id", "name"),
        CheckConstraint("quantity >= 0", name="ck_products_quantity_nonneg"),
        CheckConstraint("reorder_level >= 0", name="ck_products_reorder_level_nonneg"),
    )
