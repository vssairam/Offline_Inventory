from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(String(50), nullable=False, default="low_stock")
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    email_sent = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="alerts")
    product = relationship("Product", back_populates="alerts")

    __table_args__ = (Index("ix_alerts_user_read", "user_id", "is_read"),)
