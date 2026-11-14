from pydantic import BaseModel


class StockItem(BaseModel):
    id: int
    name: str
    sku: str
    quantity: int
    reorder_level: int
    is_low: bool


class StockList(BaseModel):
    items: list[StockItem]
    total: int
    page: int
    page_size: int
