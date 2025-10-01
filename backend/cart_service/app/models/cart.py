from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
# Remove ForeignKey and relationship imports
# from sqlalchemy.orm import relationship
from app.core.database import Base

class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user_id = Column(String(255), nullable=False, unique=True)  # Remove ForeignKey constraint
    
    # Remove all relationships
    # items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    # promo_codes = relationship("CartPromoCode", back_populates="cart", cascade="all, delete-orphan")
    # user = relationship("User", back_populates="carts")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    cart_id = Column(Integer, nullable=False)  # Remove ForeignKey constraint
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, CheckConstraint('quantity > 0'), nullable=False, default=1)
    
    # Remove relationship
    # cart = relationship("Cart", back_populates="items")

class Wishlist(Base):
    __tablename__ = "wishlists"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user_id = Column(String(255), nullable=False, unique=True)  # Remove ForeignKey constraint
    
    # Remove relationships
    # items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")
    # user = relationship("User", back_populates="wishlists")

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    wishlist_id = Column(Integer, nullable=False)  # Remove ForeignKey constraint
    product_id = Column(Integer, nullable=False)
    
    # Remove relationship
    # wishlist = relationship("Wishlist", back_populates="items")

class PromoCode(Base):
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    code = Column(String(50), unique=True, nullable=False)
    discount_type = Column(String(20), nullable=False)  # 'percentage' or 'fixed_amount'
    discount_value = Column(Numeric(10, 2), nullable=False)
    minimum_order_value = Column(Numeric(10, 2), default=0)
    max_uses = Column(Integer)
    used_count = Column(Integer, default=0)
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Remove relationship
    # cart_promo_codes = relationship("CartPromoCode", back_populates="promo_code", cascade="all, delete-orphan")

class CartPromoCode(Base):
    __tablename__ = "cart_promo_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, nullable=False)  # Remove ForeignKey constraint
    promo_code_id = Column(Integer, nullable=False)  # Remove ForeignKey constraint
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Remove relationships
    # cart = relationship("Cart", back_populates="promo_codes")
    # promo_code = relationship("PromoCode", back_populates="cart_promo_codes")

    __table_args__ = (
        # Unique constraint to prevent duplicate promo codes in the same cart
        UniqueConstraint('cart_id', 'promo_code_id', name='uq_cart_promo_code'),
    )