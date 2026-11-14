from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

Name = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)
]
Sku = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)
]


class ProductBase(BaseModel):
    name: Name
    sku: Sku
    price: float = Field(ge=0, le=99999999.99)
    cost: float = Field(ge=0, le=99999999.99)
    quantity: int = Field(default=0, ge=0, le=1_000_000_000)
    reorder_level: int = Field(default=0, ge=0, le=1_000_000_000)
    category_id: int | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    is_active: bool | None = None  # None leaves the current value unchanged


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    price: float
    cost: float
    quantity: int
    reorder_level: int
    category_id: int | None
    image_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int


class ProductDeleteResponse(BaseModel):
    id: int
    deleted: bool
    deactivated: bool
