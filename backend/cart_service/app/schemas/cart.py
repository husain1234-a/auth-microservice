from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.product import ProductResponse

# Cart Models

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItemResponse(CartItemBase):
    id: int
    product: ProductResponse
    created_at: datetime
    
    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    user_id: str  # Changed from int to str
    items: List[CartItemResponse] = []
    promo_code: Optional['PromoCodeResponse'] = None
    subtotal: float = 0
    discount_amount: float = 0
    total_amount: float = 0
    total_items: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

class AddToCartRequest(CartItemBase):
    product_id: int
    quantity: int = 1

class RemoveFromCartRequest(BaseModel):
    product_id: int

class ApplyPromoCodeRequest(BaseModel):
    code: str

# Wishlist Models

class WishlistItemResponse(BaseModel):
    id: int
    product_id: int
    product: ProductResponse
    created_at: datetime
    
    class Config:
        from_attributes = True

class WishlistResponse(BaseModel):
    id: int
    user_id: str  # Changed from int to str
    items: List[WishlistItemResponse] = []
    created_at: datetime
    
    class Config:
        from_attributes = True

class AddToWishlistRequest(BaseModel):
    product_id: int

class MoveToCartRequest(BaseModel):
    product_id: int
    quantity: int = 1

# Promo Code Models

class PromoCodeBase(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    minimum_order_value: float = 0
    max_uses: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = True

class PromoCodeCreate(PromoCodeBase):
    pass

class PromoCodeResponse(PromoCodeBase):
    id: int
    used_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True

# Update forward references
CartResponse.model_rebuild()