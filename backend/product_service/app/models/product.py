from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, func, CheckConstraint

# Use a shared Base class
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, CheckConstraint('price > 0'), nullable=False)
    mrp = Column(Float, CheckConstraint('mrp > 0'))
    category_id = Column(Integer)
    image_url = Column(String(500))
    stock_quantity = Column(Integer, CheckConstraint('stock_quantity >= 0'), default=0)
    unit = Column(String(20))  # kg, gm, piece, liter
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())