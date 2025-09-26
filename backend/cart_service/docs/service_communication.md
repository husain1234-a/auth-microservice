# Service Communication Documentation

This document explains how the Cart microservice communicates with other services in the system.

## Overview

The Cart service is designed to work within a microservice architecture, communicating with the Auth service for authentication and the Product service for product information. All communication happens through the API Gateway.

## Authentication Flow

### JWT Token Validation

1. **Client Request**: Client sends HTTP request with JWT token in Authorization header
2. **API Gateway**: Routes request to Cart service
3. **Cart Service**: Extracts JWT token and validates it
4. **Security Module**: Decodes JWT token using secret key
5. **Response**: If valid, user ID is extracted and operation proceeds

```python
# In app/core/security.py
async def get_current_user_id(authorization: str = Header(...)):
    try:
        # Remove "Bearer " prefix if present
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
            
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return int(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

## Product Service Integration

### Fetching Product Information

The Cart service communicates with the Product service to retrieve product details:

1. **Cart Operation**: When adding/viewing cart items
2. **HTTP Client**: Uses aiohttp to make requests to Product service
3. **Product Service**: Returns product information
4. **Cart Service**: Processes and includes in response

```python
# In app/services/product_service.py
async def get_product(product_id: int) -> ProductResponse:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{settings.product_service_url}/api/v1/products/{product_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    return ProductResponse(**data)
                elif response.status == 404:
                    raise HTTPException(status_code=404, detail="Product not found")
                else:
                    raise HTTPException(status_code=response.status, detail="Product service error")
        except aiohttp.ClientError:
            raise HTTPException(status_code=503, detail="Product service unavailable")
```

## Database Operations

### Cart Management

The Cart service uses SQLAlchemy ORM for database operations:

1. **Database Connection**: Async PostgreSQL connection
2. **Models**: Cart and CartItem models
3. **Operations**: CRUD operations for cart management

```python
# In app/services/cart_service.py
async def add_item_to_cart(self, user_id: int, item_data: AddToCartRequest) -> Cart:
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
```

## Error Handling

### Service Communication Errors

The Cart service handles various error scenarios:

1. **Authentication Errors**: Invalid or missing JWT tokens
2. **Product Service Errors**: Product not found or service unavailable
3. **Database Errors**: Connection issues or query failures

```python
# In routes/cart.py
@router.post("/cart/add", response_model=CartResponse, summary="Add Item to Cart")
async def add_to_cart(
    item_data: AddToCartRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Add an item to the user's cart or update quantity if already exists.
    
    This endpoint adds a product to the user's shopping cart or increases
    the quantity if the product is already in the cart. It validates that
    the product exists by communicating with the Product service.
    """
    cart_service = CartService(db)
    cart = await cart_service.add_item_to_cart(user_id, item_data)
    return cart
```

## Future Integration Points

### With Auth Service

Future enhancements could include:
- User profile information retrieval
- Role-based access control
- Session management

### With Other Services

Potential future integrations:
- **Order Service**: Converting carts to orders
- **Inventory Service**: Real-time stock checking
- **Notification Service**: Cart abandonment reminders