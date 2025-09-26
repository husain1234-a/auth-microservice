"""
Cart Routes Module

This module defines the HTTP routes for cart-related operations.
It handles requests for managing user shopping carts, wishlists, and promo codes
and delegates business logic to the CartService.
"""

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.cart_service import CartService
from app.schemas.cart import (
    CartResponse, 
    AddToCartRequest, 
    RemoveFromCartRequest, 
    ApplyPromoCodeRequest,
    WishlistResponse,
    AddToWishlistRequest,
    MoveToCartRequest
)
from typing import Optional

router = APIRouter()

# Cart Routes

@router.get("/cart", response_model=CartResponse, summary="Get User's Cart")
async def get_cart(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the current user's cart with all items.
    
    This endpoint fetches the authenticated user's shopping cart,
    including all items and their associated product details.
    If the user doesn't have a cart, an empty cart is created.
    
    Args:
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        CartResponse: The user's cart with all items and product details
    """
    cart_service = CartService(db)
    cart = await cart_service.get_cart_with_items(user_id)
    return cart

@router.post("/cart/add", response_model=CartResponse, summary="Add Item to Cart")
async def add_to_cart(
    item_data: AddToCartRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Add an item to the user's cart or update quantity if already exists.
    
    This endpoint adds a product to the user's shopping cart or increases
    the quantity if the product is already in the cart. It validates that
    the product exists by communicating with the Product service.
    
    Args:
        item_data: The data for the item to add to the cart
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        CartResponse: The updated cart with all items
        
    Raises:
        HTTPException: If the product is not found (404)
    """
    cart_service = CartService(db)
    cart = await cart_service.add_item_to_cart(user_id, item_data)
    return cart

@router.post("/cart/remove", response_model=CartResponse, summary="Remove Item from Cart")
async def remove_from_cart(
    item_data: RemoveFromCartRequest,
    user_id: str = Depends(get_current_user_id),  # Changed from int to str
    db: AsyncSession = Depends(get_db)
):
    """Remove an item from the user's cart.
    
    This endpoint removes a specific product from the user's shopping cart.
    If the product is not in the cart, the cart is returned unchanged.
    
    Args:
        item_data: The data identifying which product to remove
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        CartResponse: The updated cart with all items
    """
    cart_service = CartService(db)
    cart = await cart_service.remove_item_from_cart(user_id, item_data)
    return cart

@router.delete("/cart/clear", response_model=CartResponse, summary="Clear User's Cart")
async def clear_cart(
    user_id: str = Depends(get_current_user_id),  # Changed from int to str
    db: AsyncSession = Depends(get_db)
):
    """Remove all items from the user's cart.
    
    This endpoint removes all items from the user's shopping cart,
    leaving an empty cart. The cart itself is preserved.
    
    Args:
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        CartResponse: The updated (empty) cart
    """
    cart_service = CartService(db)
    cart = await cart_service.clear_cart(user_id)
    return cart

@router.post("/cart/promo/apply", response_model=CartResponse, summary="Apply Promo Code")
async def apply_promo_code(
    promo_data: ApplyPromoCodeRequest,
    user_id: str = Depends(get_current_user_id),  # Changed from int to str
    db: AsyncSession = Depends(get_db)
):
    """Apply a promo code to the user's cart.
    
    This endpoint applies a promo code to the user's shopping cart if it's valid.
    
    Args:
        promo_data: The promo code to apply
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        CartResponse: The updated cart with promo code applied
        
    Raises:
        HTTPException: If the promo code is invalid or not found (404)
    """
    cart_service = CartService(db)
    cart = await cart_service.apply_promo_code(user_id, promo_data)
    return cart

@router.delete("/cart/promo/remove", response_model=CartResponse, summary="Remove Promo Code")
async def remove_promo_code(
    user_id: str = Depends(get_current_user_id),  # Changed from int to str
    db: AsyncSession = Depends(get_db)
):
    """Remove applied promo code from the user's cart.
    
    This endpoint removes any applied promo codes from the user's shopping cart.
    
    Args:
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        CartResponse: The updated cart with promo code removed
    """
    cart_service = CartService(db)
    cart = await cart_service.remove_promo_code(user_id)
    return cart

# Wishlist Routes

@router.get("/wishlist", response_model=WishlistResponse, summary="Get User's Wishlist")
async def get_wishlist(
    user_id: str = Depends(get_current_user_id),  # Changed from int to str
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the current user's wishlist with all items.
    
    This endpoint fetches the authenticated user's wishlist,
    including all items and their associated product details.
    If the user doesn't have a wishlist, an empty wishlist is created.
    
    Args:
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        WishlistResponse: The user's wishlist with all items and product details
    """
    cart_service = CartService(db)
    wishlist = await cart_service.get_wishlist_with_items(user_id)
    return wishlist

@router.post("/wishlist/add", response_model=WishlistResponse, summary="Add Item to Wishlist")
async def add_to_wishlist(
    item_data: AddToWishlistRequest,
    user_id: str = Depends(get_current_user_id),  # Changed from int to str
    db: AsyncSession = Depends(get_db)
):
    """Add an item to the user's wishlist.
    
    This endpoint adds a product to the user's wishlist. It validates that
    the product exists by communicating with the Product service.
    
    Args:
        item_data: The data for the item to add to the wishlist
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        WishlistResponse: The updated wishlist with all items
        
    Raises:
        HTTPException: If the product is not found (404)
    """
    cart_service = CartService(db)
    wishlist = await cart_service.add_item_to_wishlist(user_id, item_data)
    return wishlist

@router.post("/wishlist/remove", response_model=WishlistResponse, summary="Remove Item from Wishlist")
async def remove_from_wishlist(
    item_data: RemoveFromCartRequest,
    user_id: str = Depends(get_current_user_id),  # Changed from int to str
    db: AsyncSession = Depends(get_db)
):
    """Remove an item from the user's wishlist.
    
    This endpoint removes a specific product from the user's wishlist.
    If the product is not in the wishlist, the wishlist is returned unchanged.
    
    Args:
        item_data: The data identifying which product to remove
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        WishlistResponse: The updated wishlist with all items
    """
    cart_service = CartService(db)
    wishlist = await cart_service.remove_item_from_wishlist(user_id, item_data)
    return wishlist

@router.post("/wishlist/move-to-cart", summary="Move Item from Wishlist to Cart")
async def move_to_cart(
    move_data: MoveToCartRequest,
    user_id: str = Depends(get_current_user_id),  # Changed from int to str
    db: AsyncSession = Depends(get_db)
):
    """Move an item from wishlist to cart.
    
    This endpoint moves a specific item from the user's wishlist to their cart.
    
    Args:
        move_data: The data identifying which product to move and quantity
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        dict: A message indicating success
    """
    cart_service = CartService(db)
    result = await cart_service.move_item_from_wishlist_to_cart(user_id, move_data)
    return result

@router.delete("/wishlist/clear", summary="Clear User's Wishlist")
async def clear_wishlist(
    user_id: str = Depends(get_current_user_id),  # Changed from int to str
    db: AsyncSession = Depends(get_db)
):
    """Remove all items from the user's wishlist.
    
    This endpoint removes all items from the user's wishlist.
    
    Args:
        user_id: The ID of the authenticated user (extracted from JWT token)
        db: Database session dependency
        
    Returns:
        dict: A message indicating success
    """
    cart_service = CartService(db)
    result = await cart_service.clear_wishlist(user_id)
    return result