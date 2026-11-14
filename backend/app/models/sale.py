from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    total_amount = Column(Numeric(12, 2), nullable=False)
    sold_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="sales")
    items = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(
        Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sale_items_quantity_pos"),
    )
