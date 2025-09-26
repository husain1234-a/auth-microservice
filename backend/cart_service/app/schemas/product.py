from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    mrp: Optional[float] = None
    category_id: int
    image_url: Optional[str] = None
    stock_quantity: int = 0
    unit: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True