"""Dashboard and admin schemas."""

import datetime as dt

from pydantic import BaseModel, ConfigDict


class TrendPoint(BaseModel):
    date: dt.date
    revenue: float


class LowStockItem(BaseModel):
    id: int
    name: str
    sku: str
    quantity: int
    reorder_level: int
    deficit: int


class DashboardSummary(BaseModel):
    total_products: int
    low_stock_count: int
    total_stock_value: float
    sales_today_count: int
    sales_today_revenue: float
    revenue_30d: float
    profit_30d: float
    trend: list[TrendPoint]
    low_stock_items: list[LowStockItem]


class AdminUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str | None = None
    is_active: bool
    is_admin: bool
    created_at: dt.datetime | None = None


class AdminUserList(BaseModel):
    items: list[AdminUser]
    total: int
    page: int
    page_size: int


class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    is_admin: bool | None = None


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_products: int
    total_sales: int
    total_revenue: float
