from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
# Remove relationship import
# from sqlalchemy.orm import relationship

# Use a shared Base class
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    image_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Remove the relationship to Product
    # products = relationship("Product", back_populates="category")