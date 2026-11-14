from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str | None = None
    type: str
    message: str
    is_read: bool
    email_sent: bool
    created_at: datetime


class AlertList(BaseModel):
    items: list[AlertRead]
    total: int
    page: int
    page_size: int
    unread_count: int
