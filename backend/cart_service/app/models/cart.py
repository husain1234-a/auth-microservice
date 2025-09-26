from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint, UniqueConstraint, String, Boolean, DateTime, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Cart(BaseModel):
    __tablename__ = "carts"
    
    user_id = Column(String(255), ForeignKey("users.uid", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Relationships
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    promo_codes = relationship("CartPromoCode", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id})>"

class CartItem(BaseModel):
    __tablename__ = "cart_items"
    
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, CheckConstraint('quantity > 0'), nullable=False, default=1)
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    
    __table_args__ = (
        # Unique constraint to prevent duplicate products in the same cart
        UniqueConstraint('cart_id', 'product_id', name='uq_cart_item'),
    )
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, product_id={self.product_id}, quantity={self.quantity})>"

class Wishlist(BaseModel):
    __tablename__ = "wishlists"
    
    user_id = Column(String(255), ForeignKey("users.uid", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Relationships
    items = relationship("WishlistItem", back_populates="wishlist", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Wishlist(id={self.id}, user_id={self.user_id})>"

class WishlistItem(BaseModel):
    __tablename__ = "wishlist_items"
    
    wishlist_id = Column(Integer, ForeignKey("wishlists.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    wishlist = relationship("Wishlist", back_populates="items")
    
    __table_args__ = (
        # Unique constraint to prevent duplicate products in the same wishlist
        UniqueConstraint('wishlist_id', 'product_id', name='uq_wishlist_item'),
    )
    
    def __repr__(self):
        return f"<WishlistItem(id={self.id}, wishlist_id={self.wishlist_id}, product_id={self.product_id})>"

class PromoCode(BaseModel):
    __tablename__ = "promo_codes"
    
    code = Column(String(50), unique=True, nullable=False)
    discount_type = Column(String(20), nullable=False)  # 'percentage' or 'fixed_amount'
    discount_value = Column(Numeric(10, 2), nullable=False)
    minimum_order_value = Column(Numeric(10, 2), default=0)
    max_uses = Column(Integer)
    used_count = Column(Integer, default=0)
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    cart_promo_codes = relationship("CartPromoCode", back_populates="promo_code", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint('discount_value > 0', name='check_discount_value_positive'),
        CheckConstraint('minimum_order_value >= 0', name='check_minimum_order_value_non_negative'),
        CheckConstraint('max_uses IS NULL OR max_uses > 0', name='check_max_uses_positive'),
        CheckConstraint('used_count >= 0', name='check_used_count_non_negative'),
    )
    
    def __repr__(self):
        return f"<PromoCode(id={self.id}, code={self.code}, discount_type={self.discount_type}, discount_value={self.discount_value})>"

class CartPromoCode(BaseModel):
    __tablename__ = "cart_promo_codes"
    
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
    promo_code_id = Column(Integer, ForeignKey("promo_codes.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    cart = relationship("Cart", back_populates="promo_codes")
    promo_code = relationship("PromoCode", back_populates="cart_promo_codes")
    
    __table_args__ = (
        # Unique constraint to prevent duplicate promo codes in the same cart
        UniqueConstraint('cart_id', 'promo_code_id', name='uq_cart_promo_code'),
    )
    
    def __repr__(self):
        return f"<CartPromoCode(id={self.id}, cart_id={self.cart_id}, promo_code_id={self.promo_code_id})>"