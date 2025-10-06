from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, CheckConstraint
from sqlalchemy.sql import func
from app.models.base import Base
from typing import List, Optional
from enum import Enum

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

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)
    delivery_partner_id = Column(String(255), nullable=True)
    total_amount = Column(Numeric(10, 2), CheckConstraint('total_amount > 0'), nullable=False)
    delivery_fee = Column(Numeric(10, 2), CheckConstraint('delivery_fee >= 0'), default=0)
    status = Column(String(20), default=OrderStatus.PENDING)
    delivery_address = Column(Text, nullable=False)
    delivery_latitude = Column(String(20), nullable=True)
    delivery_longitude = Column(String(20), nullable=True)
    estimated_delivery_time = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Removed relationships to avoid joins
    
    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id}, status={self.status})>"

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, CheckConstraint('quantity > 0'), nullable=False)
    price = Column(Numeric(10, 2), CheckConstraint('price > 0'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Removed relationships to avoid joins
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, quantity={self.quantity})>"

class OrderTemplate(Base):
    __tablename__ = "order_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)
    name = Column(String(100), nullable=True)
    items = Column(Text, nullable=False)  # JSON string representation of items
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Removed relationships to avoid joins
    
    def __repr__(self):
        return f"<OrderTemplate(id={self.id}, user_id={self.user_id}, name={self.name})>"

class OrderFeedback(Base):
    __tablename__ = "order_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    rating = Column(Integer, CheckConstraint('rating >= 1 AND rating <= 5'), nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Removed relationships to avoid joins
    
    def __repr__(self):
        return f"<OrderFeedback(id={self.id}, order_id={self.order_id}, rating={self.rating})>"