from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base

class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user_id = Column(String(255), nullable=False, unique=True)
    
    # Removed relationships to avoid joins
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id})>"

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    cart_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, CheckConstraint('quantity > 0'), nullable=False, default=1)
    
    # Removed relationships to avoid joins
    
    __table_args__ = (
        # Unique constraint to prevent duplicate products in the same cart
        UniqueConstraint('cart_id', 'product_id', name='uq_cart_item'),
    )
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, product_id={self.product_id}, quantity={self.quantity})>"

class Wishlist(Base):
    __tablename__ = "wishlists"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user_id = Column(String(255), nullable=False, unique=True)
    
    # Removed relationships to avoid joins
    
    def __repr__(self):
        return f"<Wishlist(id={self.id}, user_id={self.user_id})>"

class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    wishlist_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    
    # Removed relationships to avoid joins
    
    __table_args__ = (
        # Unique constraint to prevent duplicate products in the same wishlist
        UniqueConstraint('wishlist_id', 'product_id', name='uq_wishlist_item'),
    )
    
    def __repr__(self):
        return f"<WishlistItem(id={self.id}, wishlist_id={self.wishlist_id}, product_id={self.product_id})>"

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
    
    # Removed relationships to avoid joins
    
    __table_args__ = (
        CheckConstraint('discount_value > 0', name='check_discount_value_positive'),
        CheckConstraint('minimum_order_value >= 0', name='check_minimum_order_value_non_negative'),
        CheckConstraint('max_uses IS NULL OR max_uses > 0', name='check_max_uses_positive'),
        CheckConstraint('used_count >= 0', name='check_used_count_non_negative'),
    )
    
    def __repr__(self):
        return f"<PromoCode(id={self.id}, code={self.code}, discount_type={self.discount_type}, discount_value={self.discount_value})>"

class CartPromoCode(Base):
    __tablename__ = "cart_promo_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, nullable=False)
    promo_code_id = Column(Integer, nullable=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Removed relationships to avoid joins
    
    __table_args__ = (
        # Unique constraint to prevent duplicate promo codes in the same cart
        UniqueConstraint('cart_id', 'promo_code_id', name='uq_cart_promo_code'),
    )
    
    def __repr__(self):
        return f"<CartPromoCode(id={self.id}, cart_id={self.cart_id}, promo_code_id={self.promo_code_id})>"