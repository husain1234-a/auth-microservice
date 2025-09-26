from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.cart import Cart, CartItem, Wishlist, WishlistItem, PromoCode, CartPromoCode
from app.schemas.cart import (
    AddToCartRequest, 
    RemoveFromCartRequest, 
    ApplyPromoCodeRequest, 
    AddToWishlistRequest, 
    MoveToCartRequest
)
from app.services.product_service import ProductService
from fastapi import HTTPException

class CartService:
    """Service class for handling cart-related operations.
    
    This service provides methods for managing user shopping carts,
    including adding items, removing items, and retrieving cart information.
    It also handles wishlist and promo code functionality.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize the CartService with a database session.
        
        Args:
            db: An async database session for interacting with the database
        """
        self.db = db
        
    # Cart Methods
    
    async def get_or_create_cart(self, user_id: str) -> Cart:
        """Get existing cart for user or create a new one.
        
        Args:
            user_id: The ID of the user whose cart to retrieve or create
            
        Returns:
            Cart: The user's cart object
        """
        result = await self.db.execute(select(Cart).where(Cart.user_id == user_id))
        cart = result.scalar_one_or_none()
        
        if not cart:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart)
            
        return cart
    
    async def get_or_create_wishlist(self, user_id: str) -> Wishlist:
        """Get existing wishlist for user or create a new one.
        
        Args:
            user_id: The ID of the user whose wishlist to retrieve or create
            
        Returns:
            Wishlist: The user's wishlist object
        """
        result = await self.db.execute(select(Wishlist).where(Wishlist.user_id == user_id))
        wishlist = result.scalar_one_or_none()
        
        if not wishlist:
            wishlist = Wishlist(user_id=user_id)
            self.db.add(wishlist)
            await self.db.commit()
            await self.db.refresh(wishlist)
            
        return wishlist
    
    async def get_cart_with_items(self, user_id: str) -> Cart:
        """Get user's cart with all items and product details.
        
        This method retrieves a user's cart and populates it with all items.
        It also fetches product details for each item from the Product service
        and calculates cart totals.
        
        Args:
            user_id: The ID of the user whose cart to retrieve
            
        Returns:
            Cart: The user's cart with items and product details
        """
        cart = await self.get_or_create_cart(user_id)
        
        # Load cart with items using selectinload to avoid lazy loading issues
        result = await self.db.execute(
            select(Cart)
            .options(selectinload(Cart.items))
            .where(Cart.id == cart.id)
        )
        cart_with_items = result.scalar_one()
        
        # Use the cart with properly loaded items
        cart = cart_with_items
        
        # Load applied promo codes
        promo_result = await self.db.execute(
            select(CartPromoCode).where(CartPromoCode.cart_id == cart.id)
        )
        cart_promo_codes = promo_result.scalars().all()
        
        # Load product details for each item
        total_amount = 0
        for item in cart.items:
            try:
                product = await ProductService.get_product(item.product_id)
                # This is a simplified approach - in a real app, you might want to store
                # product details in the cart item to avoid calling the product service
                # every time the cart is retrieved
                setattr(item, 'product', product)
                total_amount += product.price * item.quantity
            except HTTPException:
                # If product is not found, we might want to remove it from the cart
                # For now, we'll just skip it
                pass
        
        # Calculate totals
        cart.subtotal = total_amount
        cart.total_items = sum(item.quantity for item in cart.items)
        
        # Apply promo code discount if any
        if cart_promo_codes:
            # For simplicity, we're only handling one promo code
            cart_promo_code = cart_promo_codes[0]
            promo_result = await self.db.execute(
                select(PromoCode).where(PromoCode.id == cart_promo_code.promo_code_id)
            )
            promo_code = promo_result.scalar_one_or_none()
            
            if promo_code:
                # Refresh the promo_code to get actual values instead of Column objects
                await self.db.refresh(promo_code)
                
                # Extract values using getattr to avoid SQLAlchemy column expression issues
                is_active = getattr(promo_code, 'is_active', False)
                discount_type = getattr(promo_code, 'discount_type', '')
                discount_value = float(str(getattr(promo_code, 'discount_value', 0)))
                minimum_order_value = float(str(getattr(promo_code, 'minimum_order_value', 0) or 0))
                
                if is_active:
                    # Check if promo code is valid based on minimum order value
                    if cart.subtotal >= minimum_order_value:
                        # Calculate discount
                        if discount_type == "percentage":
                            cart.discount_amount = cart.subtotal * (discount_value / 100)
                        elif discount_type == "fixed_amount":  # Updated to match schema
                            cart.discount_amount = min(discount_value, cart.subtotal)
                        
                        cart.total_amount = cart.subtotal - cart.discount_amount
                        setattr(cart, 'promo_code', promo_code)
                    else:
                        cart.total_amount = cart.subtotal
                else:
                    cart.total_amount = cart.subtotal
            else:
                cart.total_amount = cart.subtotal
        else:
            cart.total_amount = cart.subtotal
            cart.discount_amount = 0
        
        return cart
    
    async def add_item_to_cart(self, user_id: str, item_data: AddToCartRequest) -> Cart:
        """Add an item to the user's cart or update quantity if already exists.
        
        This method adds a new item to the user's cart or increases the quantity
        if the item already exists in the cart. It first verifies that the
        product exists by calling the Product service.
        
        Args:
            user_id: The ID of the user whose cart to modify
            item_data: The data for the item to add to the cart
            
        Returns:
            Cart: The updated cart with all items
            
        Raises:
            HTTPException: If the product is not found (404)
        """
        # First, verify the product exists
        try:
            product = await ProductService.get_product(item_data.product_id)
        except HTTPException:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get or create cart
        cart = await self.get_or_create_cart(user_id)
        
        # Check if item already exists in cart
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == item_data.product_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if cart_item:
            # Update quantity using setattr to avoid SQLAlchemy column expression issues
            new_quantity = cart_item.quantity + item_data.quantity
            setattr(cart_item, 'quantity', new_quantity)
        else:
            # Create new cart item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity
            )
            self.db.add(cart_item)
        
        await self.db.commit()
        await self.db.refresh(cart_item)
        
        # Return updated cart
        return await self.get_cart_with_items(user_id)
    
    async def remove_item_from_cart(self, user_id: str, item_data: RemoveFromCartRequest) -> Cart:
        """Remove an item from the user's cart.
        
        This method removes a specific item from the user's cart based on
        the product ID. If the item doesn't exist in the cart, the cart
        is returned unchanged.
        
        Args:
            user_id: The ID of the user whose cart to modify
            item_data: The data identifying which product to remove
            
        Returns:
            Cart: The updated cart with all items
        """
        cart = await self.get_or_create_cart(user_id)
        
        # Find and remove the item
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == item_data.product_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if cart_item:
            await self.db.delete(cart_item)
            await self.db.commit()
        
        # Return updated cart
        return await self.get_cart_with_items(user_id)
    
    async def clear_cart(self, user_id: str) -> Cart:
        """Remove all items from the user's cart.
        
        This method removes all items from the user's cart, leaving an
        empty cart. The cart itself is not deleted, only the items in it.
        
        Args:
            user_id: The ID of the user whose cart to clear
            
        Returns:
            Cart: The updated (empty) cart
        """
        cart = await self.get_or_create_cart(user_id)
        
        # Delete all items in the cart
        await self.db.execute(
            CartItem.__table__.delete().where(CartItem.cart_id == cart.id)
        )
        
        # Also remove any applied promo codes
        await self.db.execute(
            CartPromoCode.__table__.delete().where(CartPromoCode.cart_id == cart.id)
        )
        
        await self.db.commit()
        
        # Return updated cart
        return await self.get_cart_with_items(user_id)
    
    async def apply_promo_code(self, user_id: str, promo_data: ApplyPromoCodeRequest) -> Cart:
        """Apply a promo code to the user's cart.
        
        This method applies a promo code to the user's cart if it's valid.
        
        Args:
            user_id: The ID of the user whose cart to modify
            promo_data: The promo code to apply
            
        Returns:
            Cart: The updated cart with promo code applied
            
        Raises:
            HTTPException: If the promo code is invalid or not found (404)
        """
        # Get or create cart
        cart = await self.get_or_create_cart(user_id)
        
        # Check if promo code exists and is valid
        result = await self.db.execute(
            select(PromoCode).where(
                and_(
                    PromoCode.code == promo_data.code,
                    PromoCode.is_active == True
                )
            )
        )
        promo_code = result.scalar_one_or_none()
        
        if not promo_code:
            raise HTTPException(status_code=404, detail="Promo code not found or inactive")
        
        # Refresh the promo_code to get actual values instead of Column objects
        await self.db.refresh(promo_code)
        
        # Extract values using getattr to avoid SQLAlchemy column expression issues
        valid_until = getattr(promo_code, 'valid_until', None)
        valid_from = getattr(promo_code, 'valid_from', None)
        max_uses = getattr(promo_code, 'max_uses', None)
        used_count = getattr(promo_code, 'used_count', 0) or 0
        
        # Check if promo code has expired
        from datetime import datetime
        if valid_until and valid_until < datetime.utcnow().replace(tzinfo=valid_until.tzinfo):
            raise HTTPException(status_code=400, detail="Promo code has expired")
        
        if valid_from and valid_from > datetime.utcnow().replace(tzinfo=valid_from.tzinfo):
            raise HTTPException(status_code=400, detail="Promo code is not yet valid")
        
        # Check if promo code has reached max uses
        if max_uses and used_count >= max_uses:
            raise HTTPException(status_code=400, detail="Promo code has reached maximum uses")
        
        # Check if promo code is already applied to this cart
        result = await self.db.execute(
            select(CartPromoCode).where(
                CartPromoCode.cart_id == cart.id,
                CartPromoCode.promo_code_id == promo_code.id
            )
        )
        existing_cart_promo = result.scalar_one_or_none()
        
        if not existing_cart_promo:
            # Apply promo code to cart
            cart_promo_code = CartPromoCode(
                cart_id=cart.id,
                promo_code_id=promo_code.id
            )
            self.db.add(cart_promo_code)
            
            # Increment used count for promo code using setattr
            new_used_count = used_count + 1
            setattr(promo_code, 'used_count', new_used_count)
            
            await self.db.commit()
            await self.db.refresh(cart_promo_code)
            await self.db.refresh(promo_code)
        
        # Return updated cart
        return await self.get_cart_with_items(user_id)
    
    async def remove_promo_code(self, user_id: str) -> Cart:
        """Remove applied promo code from the user's cart.
        
        This method removes any applied promo codes from the user's cart.
        
        Args:
            user_id: The ID of the user whose cart to modify
            
        Returns:
            Cart: The updated cart with promo code removed
        """
        # Get or create cart
        cart = await self.get_or_create_cart(user_id)
        
        # Remove all promo codes from cart
        await self.db.execute(
            CartPromoCode.__table__.delete().where(CartPromoCode.cart_id == cart.id)
        )
        
        await self.db.commit()
        
        # Return updated cart
        return await self.get_cart_with_items(user_id)
    
    # Wishlist Methods
    
    async def get_wishlist_with_items(self, user_id: str) -> Wishlist:
        """Get user's wishlist with all items and product details.
        
        This method retrieves a user's wishlist and populates it with all items.
        It also fetches product details for each item from the Product service.
        
        Args:
            user_id: The ID of the user whose wishlist to retrieve
            
        Returns:
            Wishlist: The user's wishlist with items and product details
        """
        wishlist = await self.get_or_create_wishlist(user_id)
        
        # Load wishlist with items using selectinload to avoid lazy loading issues
        result = await self.db.execute(
            select(Wishlist)
            .options(selectinload(Wishlist.items))
            .where(Wishlist.id == wishlist.id)
        )
        wishlist_with_items = result.scalar_one()
        
        # Use the wishlist with properly loaded items
        wishlist = wishlist_with_items
        
        # Load product details for each item
        for item in wishlist.items:
            try:
                product = await ProductService.get_product(item.product_id)
                setattr(item, 'product', product)
            except HTTPException:
                # If product is not found, we might want to remove it from the wishlist
                # For now, we'll just skip it
                pass
        
        return wishlist
    
    async def add_item_to_wishlist(self, user_id: str, item_data: AddToWishlistRequest) -> Wishlist:
        """Add an item to the user's wishlist.
        
        This method adds a new item to the user's wishlist. It first verifies 
        that the product exists by calling the Product service.
        
        Args:
            user_id: The ID of the user whose wishlist to modify
            item_data: The data for the item to add to the wishlist
            
        Returns:
            Wishlist: The updated wishlist with all items
            
        Raises:
            HTTPException: If the product is not found (404)
        """
        # First, verify the product exists
        try:
            product = await ProductService.get_product(item_data.product_id)
        except HTTPException:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get or create wishlist
        wishlist = await self.get_or_create_wishlist(user_id)
        
        # Check if item already exists in wishlist
        result = await self.db.execute(
            select(WishlistItem).where(
                WishlistItem.wishlist_id == wishlist.id,
                WishlistItem.product_id == item_data.product_id
            )
        )
        wishlist_item = result.scalar_one_or_none()
        
        if not wishlist_item:
            # Create new wishlist item
            wishlist_item = WishlistItem(
                wishlist_id=wishlist.id,
                product_id=item_data.product_id
            )
            self.db.add(wishlist_item)
        
        await self.db.commit()
        await self.db.refresh(wishlist_item)
        
        # Return updated wishlist
        return await self.get_wishlist_with_items(user_id)
    
    async def remove_item_from_wishlist(self, user_id: str, item_data: RemoveFromCartRequest) -> Wishlist:
        """Remove an item from the user's wishlist.
        
        This method removes a specific item from the user's wishlist based on
        the product ID. If the item doesn't exist in the wishlist, the wishlist
        is returned unchanged.
        
        Args:
            user_id: The ID of the user whose wishlist to modify
            item_data: The data identifying which product to remove
            
        Returns:
            Wishlist: The updated wishlist with all items
        """
        wishlist = await self.get_or_create_wishlist(user_id)
        
        # Find and remove the item
        result = await self.db.execute(
            select(WishlistItem).where(
                WishlistItem.wishlist_id == wishlist.id,
                WishlistItem.product_id == item_data.product_id
            )
        )
        wishlist_item = result.scalar_one_or_none()
        
        if wishlist_item:
            await self.db.delete(wishlist_item)
            await self.db.commit()
        
        # Return updated wishlist
        return await self.get_wishlist_with_items(user_id)
    
    async def move_item_from_wishlist_to_cart(self, user_id: str, move_data: MoveToCartRequest) -> dict:
        """Move an item from wishlist to cart.
        
        This method moves a specific item from the user's wishlist to their cart.
        
        Args:
            user_id: The ID of the user whose wishlist and cart to modify
            move_data: The data identifying which product to move and quantity
            
        Returns:
            dict: A message indicating success
        """
        # First, verify the product exists
        try:
            product = await ProductService.get_product(move_data.product_id)
        except HTTPException:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get or create wishlist and cart
        wishlist = await self.get_or_create_wishlist(user_id)
        cart = await self.get_or_create_cart(user_id)
        
        # Check if item exists in wishlist
        result = await self.db.execute(
            select(WishlistItem).where(
                WishlistItem.wishlist_id == wishlist.id,
                WishlistItem.product_id == move_data.product_id
            )
        )
        wishlist_item = result.scalar_one_or_none()
        
        if not wishlist_item:
            raise HTTPException(status_code=404, detail="Item not found in wishlist")
        
        # Check if item already exists in cart
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == move_data.product_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if cart_item:
            # Update quantity in cart
            new_quantity = cart_item.quantity + move_data.quantity
            setattr(cart_item, 'quantity', new_quantity)
        else:
            # Create new cart item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=move_data.product_id,
                quantity=move_data.quantity
            )
            self.db.add(cart_item)
        
        # Remove item from wishlist
        await self.db.delete(wishlist_item)
        
        await self.db.commit()
        await self.db.refresh(cart_item)
        
        return {"message": "Item moved from wishlist to cart successfully"}
    
    async def clear_wishlist(self, user_id: str) -> dict:
        """Remove all items from the user's wishlist.
        
        This method removes all items from the user's wishlist.
        
        Args:
            user_id: The ID of the user whose wishlist to clear
            
        Returns:
            dict: A message indicating success
        """
        wishlist = await self.get_or_create_wishlist(user_id)
        
        # Delete all items in the wishlist
        await self.db.execute(
            WishlistItem.__table__.delete().where(WishlistItem.wishlist_id == wishlist.id)
        )
        await self.db.commit()
        
        return {"message": "Wishlist cleared successfully"}