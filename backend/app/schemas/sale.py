"""Sale schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=1_000_000)


class SaleCreate(BaseModel):
    items: list[SaleItemCreate] = Field(min_length=1, max_length=200)
    sold_at: datetime | None = None


class SaleItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str | None = None
    quantity: int
    unit_price: float
    unit_cost: float
    line_total: float


class SaleRead(BaseModel):
    id: int
    total_amount: float
    sold_at: datetime
    created_at: datetime
    item_count: int = 0
    items: list[SaleItemRead] = []


class SaleList(BaseModel):
    items: list[SaleRead]
    total: int
    page: int
    page_size: int


class TopProduct(BaseModel):
    product_id: int
    name: str
    quantity: int
    revenue: float


class DailyPoint(BaseModel):
    date: str
    sales_count: int
    revenue: float
    profit: float


class SalesReport(BaseModel):
    total_sales_count: int
    total_revenue: float
    total_cost: float
    total_profit: float
    top_products: list[TopProduct]
    daily: list[DailyPoint]
