from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    
    uid = Column(String(255), primary_key=True)
    email = Column(String(255))
    phone_number = Column(String(20))
    display_name = Column(String(255))
    photo_url = Column(String)
    role = Column(String(50), default='customer')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships (using string references to avoid circular imports)
    carts = relationship('Cart', back_populates='user', cascade='all, delete-orphan')
    wishlists = relationship('Wishlist', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(uid={self.uid}, email={self.email}, display_name={self.display_name})>"