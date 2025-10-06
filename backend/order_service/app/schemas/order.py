from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
import json

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURN_REQUESTED = "return_requested"
    RETURN_APPROVED = "return_approved"
    PICKED_UP = "picked_up"
    REFUNDED = "refunded"

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    mrp: Optional[float] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    stock_quantity: Optional[int] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    product: Optional[ProductResponse] = None
    
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    delivery_address: str
    delivery_latitude: Optional[str] = None
    delivery_longitude: Optional[str] = None
    scheduled_for: Optional[datetime] = None

class OrderUpdate(BaseModel):
    delivery_address: Optional[str] = None
    delivery_latitude: Optional[str] = None
    delivery_longitude: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    user_id: str
    total_amount: float
    delivery_fee: float
    status: OrderStatus
    delivery_address: str
    delivery_latitude: Optional[str] = None
    delivery_longitude: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    created_at: datetime
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class AssignDeliveryPartnerRequest(BaseModel):
    delivery_partner_id: str

class OrderCancelResponse(BaseModel):
    success: bool
    message: str
    refund_initiated: bool

class OrderItemsUpdate(BaseModel):
    items: List[OrderItemCreate]

class OrderTemplateCreate(BaseModel):
    name: str
    items: List[OrderItemCreate]

class OrderTemplateResponse(BaseModel):
    id: int
    user_id: str
    name: str
    items: List[OrderItemCreate]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrderFeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class OrderFeedbackResponse(BaseModel):
    id: int
    order_id: int
    rating: Optional[int] = None
    comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class BulkStatusUpdate(BaseModel):
    order_ids: List[int]
    status: OrderStatus

class BulkAssignDelivery(BaseModel):
    order_ids: List[int]
    delivery_partner_id: str

class OrderAnalyticsResponse(BaseModel):
    date: datetime
    order_count: int
    total_revenue: float
    average_delivery_time: Optional[float] = None

class CancellationRateResponse(BaseModel):
    period: str
    cancellation_rate: float
    total_orders: int
    cancelled_orders: int

class TopCustomerResponse(BaseModel):
    user_id: str
    order_count: int
    total_spent: float