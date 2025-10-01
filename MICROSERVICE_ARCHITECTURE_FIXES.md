# Microservice Architecture Fixes Implementation Guide

This document provides detailed, actionable steps to fix the identified issues in your microservice architecture, specifically focusing on removing foreign key constraints and joins to achieve proper service independence.

## Table of Contents
1. [Overview of Issues](#overview-of-issues)
2. [Fix 1: Remove Foreign Key Constraints in Product Service](#fix-1-remove-foreign-key-constraints-in-product-service)
3. [Fix 2: Remove Foreign Key Constraints in Cart Service](#fix-2-remove-foreign-key-constraints-in-cart-service)
4. [Fix 3: Implement Service-to-Service Communication](#fix-3-implement-service-to-service-communication)
5. [Fix 4: Enhance API Gateway Authentication](#fix-4-enhance-api-gateway-authentication)
6. [Testing and Validation](#testing-and-validation)
7. [Deployment Considerations](#deployment-considerations)

## Overview of Issues

Based on the code analysis, the following critical issues need to be addressed:

1. **Product Service**: Foreign key relationship between Product and Category tables
2. **Cart Service**: Multiple foreign key relationships with cascading deletes
3. **Inter-Service Communication**: Need to replace database relationships with API calls
4. **Authentication**: Clarify and enhance the role of API Gateway vs Auth Service

## Fix 1: Remove Foreign Key Constraints in Product Service

### Current Issues
- [Product model](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/backend/product_service/app/models/product.py#L7-L22) has a foreign key constraint to Category
- ORM relationships create tight coupling between entities

### Implementation Steps

#### Step 1: Modify Product Model
File: `backend/product_service/app/models/product.py`

```python
# Before:
category_id = Column(Integer, ForeignKey('categories.id'))
category = relationship("Category", back_populates="products")

# After:
category_name = Column(String(100))  # Store category name directly
category_info = Column(JSON)         # Store additional category metadata if needed
```

#### Step 2: Modify Category Model
File: `backend/product_service/app/models/category.py`

```python
# Before:
products = relationship("Product", back_populates="category")

# After:
# Remove the relationship entirely
# No code change needed here as we're removing the relationship from Product model
```

#### Step 3: Update Product CRUD Operations
File: `backend/product_service/app/services/product_service.py`

When creating a product, instead of referencing a category ID, store category information directly:

```python
# Before (simplified):
def create_product(product_data):
    # This would rely on category_id foreign key
    product = Product(**product_data)
    db.add(product)
    db.commit()
    return product

# After:
def create_product(product_data, category_data=None):
    # Extract category information
    if category_data:
        product_data['category_name'] = category_data.get('name')
        product_data['category_info'] = category_data
    
    product = Product(**product_data)
    db.add(product)
    db.commit()
    return product
```

## Fix 2: Remove Foreign Key Constraints in Cart Service

### Current Issues
- Multiple foreign key relationships in Cart, CartItem, Wishlist, WishlistItem, CartPromoCode models
- Cascading delete relationships that create tight coupling
- User model duplicated across services

### Implementation Steps

#### Step 1: Modify Cart Model
File: `backend/cart_service/app/models/cart.py`

```python
# Before:
user_id = Column(String(255), ForeignKey("users.uid", ondelete="CASCADE"), nullable=False, unique=True)
user = relationship("User", back_populates="carts")

# After:
user_id = Column(String(255), nullable=False, unique=True)
# Remove the relationship entirely
```

#### Step 2: Modify CartItem Model
File: `backend/cart_service/app/models/cart.py`

```python
# Before:
cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
cart = relationship("Cart", back_populates="items")

# After:
cart_id = Column(Integer, nullable=False)
# Remove the relationship entirely
```

#### Step 3: Modify Wishlist Model
File: `backend/cart_service/app/models/cart.py`

```python
# Before:
user_id = Column(String(255), ForeignKey("users.uid", ondelete="CASCADE"), nullable=False, unique=True)
user = relationship("User", back_populates="wishlists")

# After:
user_id = Column(String(255), nullable=False, unique=True)
# Remove the relationship entirely
```

#### Step 4: Modify WishlistItem Model
File: `backend/cart_service/app/models/cart.py`

```python
# Before:
wishlist_id = Column(Integer, ForeignKey("wishlists.id", ondelete="CASCADE"), nullable=False)
wishlist = relationship("Wishlist", back_populates="items")

# After:
wishlist_id = Column(Integer, nullable=False)
# Remove the relationship entirely
```

#### Step 5: Modify CartPromoCode Model
File: `backend/cart_service/app/models/cart.py`

```python
# Before:
cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False)
promo_code_id = Column(Integer, ForeignKey("promo_codes.id", ondelete="CASCADE"), nullable=False)
cart = relationship("Cart", back_populates="promo_codes")
promo_code = relationship("PromoCode", back_populates="cart_promo_codes")

# After:
cart_id = Column(Integer, nullable=False)
promo_code_id = Column(Integer, nullable=False)
# Remove both relationships entirely
```

#### Step 6: Remove User Model
Since user information should come from the Auth Service, remove the User model from Cart Service:

File: `backend/cart_service/app/models/user.py`

```python
# Delete this entire file
```

## Fix 3: Implement Service-to-Service Communication

### Current Issues
- Cart Service directly references User and Product data
- Need to replace database joins with API calls

### Implementation Steps

#### Step 1: Update Product Service Client
File: `backend/cart_service/app/services/product_service.py`

```python
# Before:
async def get_product(product_id: int) -> ProductResponse:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{settings.product_service_url}/api/products/{product_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    return ProductResponse(**data)
                elif response.status == 404:
                    raise HTTPException(status_code=404, detail="Product not found")
                else:
                    raise HTTPException(status_code=response.status, detail="Product service error")
        except aiohttp.ClientError:
            raise HTTPException(status_code=503, detail="Product service unavailable")

# After (enhanced with error handling and caching):
async def get_product(product_id: int) -> ProductResponse:
    # Implement caching to reduce service calls
    cache_key = f"product_{product_id}"
    cached_product = await get_from_cache(cache_key)
    if cached_product:
        return ProductResponse(**cached_product)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{settings.product_service_url}/api/products/{product_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    # Cache for 5 minutes
                    await set_in_cache(cache_key, data, expire=300)
                    return ProductResponse(**data)
                elif response.status == 404:
                    raise HTTPException(status_code=404, detail="Product not found")
                else:
                    raise HTTPException(status_code=response.status, detail="Product service error")
        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to product service: {e}")
            raise HTTPException(status_code=503, detail="Product service unavailable")
```

#### Step 2: Implement User Service Client
Create a new file: `backend/cart_service/app/services/user_service.py`

```python
"""
User Service Client Module

This module provides a client for communicating with the Auth microservice.
It handles HTTP requests to fetch user information needed for cart operations.
"""

import aiohttp
from fastapi import HTTPException
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class UserService:
    """Service class for communicating with the Auth microservice."""
    
    @staticmethod
    async def get_user(user_id: str):
        """Fetch a user by their ID from the Auth service.
        
        Args:
            user_id: The ID of the user to fetch
            
        Returns:
            dict: The user information
            
        Raises:
            HTTPException: If the user is not found (404) or if there
                          is a service communication error (503)
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{settings.user_service_url}/auth/users/{user_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 404:
                        raise HTTPException(status_code=404, detail="User not found")
                    else:
                        raise HTTPException(status_code=response.status, detail="Auth service error")
            except aiohttp.ClientError as e:
                logger.error(f"Failed to connect to auth service: {e}")
                raise HTTPException(status_code=503, detail="Auth service unavailable")
```

#### Step 3: Update Cart Operations to Use Service Calls
File: `backend/cart_service/app/services/cart_service.py`

```python
# Before (conceptual):
def add_item_to_cart(cart_id, product_id, quantity):
    # Would directly access product and user data from database
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    product = db.query(Product).filter(Product.id == product_id).first()
    # ... rest of logic

# After:
async def add_item_to_cart(cart_id, product_id, quantity, user_id):
    # Validate user exists by calling Auth service
    try:
        user = await UserService.get_user(user_id)
    except HTTPException as e:
        raise HTTPException(status_code=400, detail="Invalid user")
    
    # Validate product exists by calling Product service
    try:
        product = await ProductService.get_product(product_id)
    except HTTPException as e:
        raise HTTPException(status_code=400, detail="Invalid product")
    
    # Proceed with adding item to cart
    cart_item = CartItem(
        cart_id=cart_id,
        product_id=product_id,
        quantity=quantity
    )
    db.add(cart_item)
    db.commit()
    return cart_item
```

## Fix 4: Enhance API Gateway Authentication

### Current Issues
- Authentication logic distributed across services
- Need to clarify Gateway vs Auth Service roles

### Implementation Steps

#### Step 1: Add JWT Validation to Gateway
File: `backend/gateway/app/middleware/auth.py` (Create new file)

```python
"""
Authentication Middleware for API Gateway

This module provides JWT validation for all protected routes.
"""

import jwt
from fastapi import Request, HTTPException
from app.config import AUTH_CONFIG

async def validate_jwt_token(request: Request):
    """Validate JWT token from Authorization header.
    
    Args:
        request: The incoming request
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    try:
        # Extract token (Bearer <token>)
        token = auth_header.split(" ")[1]
        # Decode and validate token
        payload = jwt.decode(token, AUTH_CONFIG["jwt_secret"], algorithms=[AUTH_CONFIG["jwt_algorithm"]])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### Step 2: Update Gateway Routing with Authentication
File: `backend/gateway/app/routing.py`

Add to imports:
```python
from app.middleware.auth import validate_jwt_token
```

Update the proxy_request function:
```python
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(request: Request, path: str):
    """
    Enhanced main proxy route with authentication
    """
    # ... existing code for service matching ...
    
    # Apply authentication for protected routes
    protected_prefixes = ["/cart", "/api/protected"]  # Add your protected routes
    is_protected = any(path.startswith(prefix) for prefix in protected_prefixes)
    
    user_payload = None
    if is_protected:
        user_payload = await validate_jwt_token(request)
    
    # ... existing code for request preparation ...
    
    # Add user context to headers if authenticated
    if user_payload:
        headers["X-User-ID"] = user_payload.get("uid")
        headers["X-User-Role"] = user_payload.get("role", "customer")
        headers["X-Auth-Payload"] = str(user_payload)  # Be careful with this in production
    
    # ... rest of existing code ...
```

#### Step 3: Update Service Configuration
File: `backend/gateway/app/config.py`

Add authentication configuration:
```python
# Add to existing config
AUTH_CONFIG = {
    "jwt_secret": os.getenv("JWT_SECRET", "your_default_secret_key"),
    "jwt_algorithm": "HS256"
}
```

#### Step 4: Simplify Service-Level Authentication
In each service, trust the Gateway-provided user context:

File: `backend/cart_service/app/core/security.py` (Create new file)

```python
"""
Security utilities for Cart Service

This module provides utilities for handling authentication
based on Gateway-provided context.
"""

from fastapi import Request, HTTPException

def get_current_user(request: Request):
    """Extract user information from Gateway-provided headers.
    
    Args:
        request: The incoming request with Gateway headers
        
    Returns:
        dict: User information
        
    Raises:
        HTTPException: If user context is missing for protected routes
    """
    user_id = request.headers.get("X-User-ID")
    user_role = request.headers.get("X-User-Role")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="User context missing")
    
    return {
        "uid": user_id,
        "role": user_role or "customer"
    }
```

## Testing and Validation

### Unit Testing Strategy

#### 1. Product Service Testing
- Test product creation without category foreign key
- Test product retrieval with embedded category data
- Verify no database constraint violations

#### 2. Cart Service Testing
- Test cart operations without database relationships
- Test service calls to Product and Auth services
- Verify proper error handling for service unavailability

#### 3. Integration Testing
- Test end-to-end workflows through API Gateway
- Validate authentication flow
- Test service communication under various failure scenarios

### Test Implementation Examples

#### Product Service Tests
File: `backend/product_service/tests/test_models.py`

```python
def test_product_creation_without_fk():
    """Test creating a product without foreign key constraints."""
    product_data = {
        "name": "Test Product",
        "description": "A test product",
        "price": 10.99,
        "category_name": "Electronics",  # Instead of category_id
        "category_info": {"department": "Tech"}  # Additional metadata
    }
    
    product = Product(**product_data)
    assert product.name == "Test Product"
    assert product.category_name == "Electronics"
    # No foreign key constraint should be violated
```

#### Cart Service Tests
File: `backend/cart_service/tests/test_services.py`

```python
import pytest
from unittest.mock import patch, AsyncMock
from app.services.cart_service import add_item_to_cart

@pytest.mark.asyncio
@patch('app.services.cart_service.UserService.get_user')
@patch('app.services.cart_service.ProductService.get_product')
async def test_add_item_to_cart_with_valid_data(mock_get_product, mock_get_user):
    """Test adding item to cart with valid user and product."""
    # Mock service responses
    mock_get_user.return_value = {"uid": "user123", "role": "customer"}
    mock_get_product.return_value = {"id": 1, "name": "Test Product", "price": 10.99}
    
    # Test the function
    result = await add_item_to_cart(cart_id=1, product_id=1, quantity=2, user_id="user123")
    
    # Verify service calls were made
    mock_get_user.assert_called_once_with("user123")
    mock_get_product.assert_called_once_with(1)
    
    # Verify result
    assert result.cart_id == 1
    assert result.product_id == 1
    assert result.quantity == 2
```

## Deployment Considerations

### 1. Data Migration
Before deploying these changes, you'll need to migrate existing data:

#### Product Data Migration
```sql
-- Add new columns to products table
ALTER TABLE products ADD COLUMN category_name VARCHAR(100);
ALTER TABLE products ADD COLUMN category_info JSON;

-- Populate new columns with existing data
UPDATE products 
SET category_name = (SELECT name FROM categories WHERE categories.id = products.category_id),
    category_info = (SELECT row_to_json(categories) FROM categories WHERE categories.id = products.category_id);

-- Remove foreign key constraint
ALTER TABLE products DROP CONSTRAINT products_category_id_fkey;
ALTER TABLE products DROP COLUMN category_id;

-- Remove relationship from categories table
-- (No specific column to drop, just remove the ORM relationship)
```

#### Cart Data Migration
```sql
-- For all tables with foreign key constraints, remove them:
-- carts table
ALTER TABLE carts DROP CONSTRAINT carts_user_id_fkey;

-- cart_items table
ALTER TABLE cart_items DROP CONSTRAINT cart_items_cart_id_fkey;

-- Similar for other tables with foreign key constraints
```

### 2. Environment Configuration
Update your `.env` files with new configuration:

File: `backend/gateway/.env`
```env
JWT_SECRET=your_super_secret_key_here
AUTH_SERVICE_URL=http://auth-service:8001
PRODUCT_SERVICE_URL=http://product-service:8002
CART_SERVICE_URL=http://cart-service:8003
```

### 3. Docker Compose Updates
File: `docker-compose.yml`

Ensure services have proper environment variables:
```yaml
gateway:
  build: ./backend/gateway
  ports:
    - "8000:8000"
  environment:
    - AUTH_SERVICE_URL=http://auth-service:8001
    - PRODUCT_SERVICE_URL=http://product-service:8002
    - CART_SERVICE_URL=http://cart-service:8003
    - JWT_SECRET=your_super_secret_key_here  # Add this
  depends_on:
    - auth-service
    - product-service
    - cart-service
```

### 4. Rollout Strategy
1. **Blue-Green Deployment**:
   - Deploy new version alongside existing services
   - Route a small percentage of traffic to new version
   - Gradually increase traffic as confidence grows

2. **Feature Flags**:
   - Implement feature flags to enable/disable new functionality
   - Allow quick rollback if issues are detected

3. **Monitoring**:
   - Set up comprehensive logging and monitoring
   - Monitor error rates, response times, and service health
   - Set up alerts for anomalies

## Conclusion

This implementation guide provides a comprehensive approach to fixing the identified issues in your microservice architecture:

1. **Removed database-level coupling** by eliminating foreign key constraints
2. **Implemented proper service-to-service communication** through API calls
3. **Enhanced authentication** with centralized validation at the Gateway
4. **Provided testing strategies** to ensure reliability
5. **Outlined deployment considerations** for smooth migration

Following these steps will result in a more robust, scalable, and maintainable microservice architecture that adheres to best practices while maintaining all existing functionality.