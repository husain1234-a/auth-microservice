# Product Microservice Specification

## Overview
This document outlines the requirements and API endpoints for a standalone Product microservice that will be extracted from the current monolithic application. The microservice will handle all product-related functionality including product management, categories, and inventory.

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Serialization**: Pydantic
- **Authentication**: JWT-based (to be implemented)
- **Image Storage**: Cloudflare R2 (S3-compatible)
- **Image Processing**: Pillow
- **Deployment**: Docker containerized

## Database Schema

### Category Table
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Product Table
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price FLOAT CHECK (price > 0) NOT NULL,
    mrp FLOAT CHECK (mrp > 0),
    category_id INTEGER REFERENCES categories(id),
    image_url VARCHAR(500),
    stock_quantity INTEGER CHECK (stock_quantity >= 0) DEFAULT 0,
    unit VARCHAR(20),  -- kg, gm, piece, liter
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_product_category_active ON products(category_id, is_active);
CREATE INDEX idx_product_name_search ON products(name);
```

## API Endpoints

### Categories

#### Get All Categories
- **Endpoint**: `GET /api/categories`
- **Description**: Retrieve all active product categories
- **Response**: 
  ```json
  [
    {
      "id": 1,
      "name": "Fruits",
      "image_url": "https://example.com/fruits.jpg",
      "is_active": true,
      "created_at": "2023-01-01T00:00:00Z"
    }
  ]
  ```

#### Get Category by ID
- **Endpoint**: `GET /api/categories/{category_id}`
- **Description**: Retrieve a specific category by its ID
- **Response**:
  ```json
  {
    "id": 1,
    "name": "Fruits",
    "image_url": "https://example.com/fruits.jpg",
    "is_active": true,
    "created_at": "2023-01-01T00:00:00Z"
  }
  ```

#### Create New Category (Admin Only)
- **Endpoint**: `POST /api/categories`
- **Description**: Create a new product category (Admin only)
- **Authentication**: Required - JWT token with "admin" role
- **Request Body**:
  ```json
  {
    "name": "Vegetables",
    "image": "binary_image_data"  // Optional: image file upload
  }
  ```
- **Response**:
  ```json
  {
    "id": 2,
    "name": "Vegetables",
    "image_url": "https://r2.cloudflare.com/bucket/categories/2.jpg",
    "is_active": true,
    "created_at": "2023-01-02T00:00:00Z"
  }
  ```

#### Update Category (Admin Only)
- **Endpoint**: `PUT /api/categories/{category_id}`
- **Description**: Update an existing product category (Admin only)
- **Authentication**: Required - JWT token with "admin" role
- **Request Body**:
  ```json
  {
    "name": "Organic Vegetables",
    "image": "binary_image_data",  // Optional: new image file upload
    "is_active": true
  }
  ```
- **Response**:
  ```json
  {
    "id": 2,
    "name": "Organic Vegetables",
    "image_url": "https://r2.cloudflare.com/bucket/categories/2.jpg",
    "is_active": true,
    "created_at": "2023-01-02T00:00:00Z"
  }
  ```

### Products

#### Get All Products
- **Endpoint**: `GET /api/products`
- **Description**: Retrieve all active products with optional filtering and pagination
- **Query Parameters**:
  - `category_id` (optional): Filter by category ID
  - `search` (optional): Search products by name
  - `limit` (optional, default=50, max=100): Maximum number of products to return
  - `offset` (optional, default=0): Number of products to skip for pagination
- **Response**:
  ```json
  [
    {
      "id": 1,
      "name": "Apple",
      "description": "Fresh red apples",
      "price": 2.99,
      "mrp": 3.99,
      "category_id": 1,
      "image_url": "https://r2.cloudflare.com/bucket/products/1.jpg",
      "stock_quantity": 100,
      "unit": "kg",
      "is_active": true,
      "created_at": "2023-01-01T00:00:00Z",
      "category": {
        "id": 1,
        "name": "Fruits",
        "image_url": "https://r2.cloudflare.com/bucket/categories/1.jpg",
        "is_active": true,
        "created_at": "2023-01-01T00:00:00Z"
      }
    }
  ]
  ```

#### Get Product by ID
- **Endpoint**: `GET /api/products/{product_id}`
- **Description**: Retrieve a specific product by its ID
- **Response**:
  ```json
  {
    "id": 1,
    "name": "Apple",
    "description": "Fresh red apples",
    "price": 2.99,
    "mrp": 3.99,
    "category_id": 1,
    "image_url": "https://r2.cloudflare.com/bucket/products/1.jpg",
    "stock_quantity": 100,
    "unit": "kg",
    "is_active": true,
    "created_at": "2023-01-01T00:00:00Z",
    "category": {
      "id": 1,
      "name": "Fruits",
      "image_url": "https://r2.cloudflare.com/bucket/categories/1.jpg",
      "is_active": true,
      "created_at": "2023-01-01T00:00:00Z"
    }
  }
  ```

#### Create New Product (Admin Only)
- **Endpoint**: `POST /api/products`
- **Description**: Create a new product (Admin only)
- **Authentication**: Required - JWT token with "admin" role
- **Request Body**:
  ```json
  {
    "name": "Banana",
    "description": "Fresh yellow bananas",
    "price": 1.99,
    "mrp": 2.49,
    "category_id": 1,
    "image": "binary_image_data",  // Optional: image file upload
    "stock_quantity": 50,
    "unit": "kg"
  }
  ```
- **Response**:
  ```json
  {
    "id": 2,
    "name": "Banana",
    "description": "Fresh yellow bananas",
    "price": 1.99,
    "mrp": 2.49,
    "category_id": 1,
    "image_url": "https://r2.cloudflare.com/bucket/products/2.jpg",
    "stock_quantity": 50,
    "unit": "kg",
    "is_active": true,
    "created_at": "2023-01-02T00:00:00Z",
    "category": {
      "id": 1,
      "name": "Fruits",
      "image_url": "https://r2.cloudflare.com/bucket/categories/1.jpg",
      "is_active": true,
      "created_at": "2023-01-01T00:00:00Z"
    }
  }
  ```

#### Update Product (Admin Only)
- **Endpoint**: `PUT /api/products/{product_id}`
- **Description**: Update an existing product (Admin only)
- **Authentication**: Required - JWT token with "admin" role
- **Request Body**:
  ```json
  {
    "name": "Organic Banana",
    "description": "Fresh organic yellow bananas",
    "price": 2.49,
    "mrp": 2.99,
    "category_id": 1,
    "image": "binary_image_data",  // Optional: new image file upload
    "stock_quantity": 30,
    "unit": "kg",
    "is_active": true
  }
  ```
- **Response**:
  ```json
  {
    "id": 2,
    "name": "Organic Banana",
    "description": "Fresh organic yellow bananas",
    "price": 2.49,
    "mrp": 2.99,
    "category_id": 1,
    "image_url": "https://r2.cloudflare.com/bucket/products/2.jpg",
    "stock_quantity": 30,
    "unit": "kg",
    "is_active": true,
    "created_at": "2023-01-02T00:00:00Z",
    "updated_at": "2023-01-03T00:00:00Z",
    "category": {
      "id": 1,
      "name": "Fruits",
      "image_url": "https://r2.cloudflare.com/bucket/categories/1.jpg",
      "is_active": true,
      "created_at": "2023-01-01T00:00:00Z"
    }
  }
  ```

#### Delete Product (Admin Only)
- **Endpoint**: `DELETE /api/products/{product_id}`
- **Description**: Delete a product (soft delete - set is_active to false) (Admin only)
- **Authentication**: Required - JWT token with "admin" role
- **Response**:
  ```json
  {
    "message": "Product deleted successfully"
  }
  ```

## Data Models

### Category Models

#### CategoryBase
```python
class CategoryBase(BaseModel):
    name: str
```

#### CategoryCreate
```python
class CategoryCreate(CategoryBase):
    image: Optional[UploadFile] = None
```

#### CategoryUpdate
```python
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    image: Optional[UploadFile] = None
    is_active: Optional[bool] = None
```

#### CategoryResponse
```python
class CategoryResponse(CategoryBase):
    id: int
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Product Models

#### ProductBase
```python
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    mrp: Optional[float] = None
    category_id: int
    stock_quantity: int = 0
    unit: Optional[str] = None
```

#### ProductCreate
```python
class ProductCreate(ProductBase):
    image: Optional[UploadFile] = None
```

#### ProductUpdate
```python
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    mrp: Optional[float] = None
    category_id: Optional[int] = None
    image: Optional[UploadFile] = None
    stock_quantity: Optional[int] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None
```

#### ProductResponse
```python
class ProductResponse(ProductBase):
    id: int
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: Optional[CategoryResponse] = None
    
    class Config:
        from_attributes = True
```

## Image Processing and Storage

### Image Compression
Before uploading images to Cloudflare R2, the service will compress images to optimize storage and bandwidth usage:

1. **JPEG Images**: Compressed to 80% quality
2. **PNG Images**: Converted to JPEG format and compressed to 80% quality
3. **Maximum Dimensions**: Images will be resized to a maximum of 1200x1200 pixels while maintaining aspect ratio
4. **Thumbnail Generation**: A thumbnail (300x300) will be generated for each image

### R2 Bucket Integration

#### Configuration
The service requires the following environment variables for R2 integration:
```env
R2_ENDPOINT_URL=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET_NAME=product-images
R2_REGION=auto
```

#### Upload Process
1. **Image Validation**: Validate file type (JPEG, PNG) and size (max 10MB)
2. **Image Compression**: Compress and resize the image as per specifications
3. **Filename Generation**: Generate a unique filename using UUID
4. **Upload to R2**: Upload the compressed image to the R2 bucket
5. **URL Storage**: Store the R2 URL in the database
6. **Error Handling**: Handle upload failures gracefully

#### Error Handling
- **Network Failures**: Retry mechanism with exponential backoff (max 3 retries)
- **Authentication Errors**: Log and alert for configuration issues
- **Storage Limitations**: Return appropriate error codes to the client
- **Invalid Files**: Validate file types and sizes before processing

#### Implementation Example
```python
import boto3
from PIL import Image
import io
import uuid
from botocore.exceptions import ClientError

class ImageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name=settings.R2_REGION
        )
        self.bucket_name = settings.R2_BUCKET_NAME

    async def upload_image(self, file: UploadFile, folder: str) -> str:
        try:
            # Validate file
            if not self._is_valid_image(file):
                raise ValueError("Invalid image file")
            
            # Compress image
            compressed_image = await self._compress_image(file)
            
            # Generate unique filename
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            s3_key = f"{folder}/{unique_filename}"
            
            # Upload to R2
            self.s3_client.upload_fileobj(
                compressed_image,
                self.bucket_name,
                s3_key
            )
            
            # Return public URL
            return f"{settings.R2_ENDPOINT_URL}/{self.bucket_name}/{s3_key}"
            
        except ClientError as e:
            # Handle R2-specific errors
            raise Exception(f"Failed to upload image to R2: {str(e)}")
        except Exception as e:
            # Handle other errors
            raise Exception(f"Failed to process image: {str(e)}")

    def _is_valid_image(self, file: UploadFile) -> bool:
        # Check file extension and size
        allowed_extensions = ['jpg', 'jpeg', 'png']
        file_extension = file.filename.split('.')[-1].lower()
        return (file_extension in allowed_extensions and 
                file.size <= 10 * 1024 * 1024)  # 10MB limit

    async def _compress_image(self, file: UploadFile) -> io.BytesIO:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Resize if larger than 1200x1200
        if image.width > 1200 or image.height > 1200:
            image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        
        # Compress to 80% quality
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=80, optimize=True)
        output.seek(0)
        
        return output
```

## Role-Based Access Control (RBAC)

### JWT Token Structure
The microservice will use JWT tokens for authentication and authorization. The token will contain the following claims:
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "admin",  // or "user"
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Role Definitions
1. **admin**: Full access to all endpoints including create, update, and delete operations
2. **user**: Read-only access to products and categories

### Implementation Details
1. **Token Validation**: All protected endpoints will validate the JWT token using a middleware
2. **Role Check**: Endpoints requiring admin access will check for the "admin" role in the token
3. **Error Handling**: Unauthorized requests will return a 403 Forbidden status

### Security Middleware
```python
from fastapi import HTTPException, status
from jose import JWTError, jwt

def verify_admin_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

## Required Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/product_db

# JWT
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256

# App
APP_NAME=Product Service
DEBUG=True
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# Cloudflare R2
R2_ENDPOINT_URL=https://your-account.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET_NAME=product-images
R2_REGION=auto

# Security
# Add any additional security-related environment variables here
```

## Dependencies (requirements.txt)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
pydantic==2.5.0
pydantic-settings==2.0.3
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
alembic==1.12.1
passlib[bcrypt]==1.7.4
cryptography==41.0.8
boto3==1.26.137
pillow==10.1.0
```

## Project Structure

```
product-service/
├── app/
│   ├── routes/
│   │   │   ├── routes/
│   │   │   │   ├── products.py
│   │   │   │   └── categories.py
│   │   │   └── api.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── product.py
│   │   └── category.py
│   ├── schemas/
│   │   ├── product.py
│   │   └── category.py
│   ├── services/
│   │   ├── product_service.py
│   │── utils/
│   │   └── image_service.py
│   └── main.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Additional Considerations

### 1. Authentication & Authorization
- Implement JWT-based authentication
- Add role-based access control (if needed for admin operations)
- Secure endpoints that modify data

### 2. Error Handling
- Standardized error response format
- Proper HTTP status codes
- Detailed error messages for debugging

### 3. Logging & Monitoring
- Structured logging for all operations
- Request tracing with unique IDs
- Performance metrics collection

### 4. Caching
- Implement Redis caching for frequently accessed data
- Cache invalidation strategies

### 5. Rate Limiting
- Implement rate limiting to prevent abuse
- Different limits for different types of requests

### 6. Health Checks
- Basic health check endpoint
- Detailed health check with database connectivity verification

## Future Enhancements

1. **Search Functionality**: Implement full-text search using Elasticsearch or PostgreSQL's full-text search
2. **Inventory Management**: Add more sophisticated inventory tracking features
3. **Product Variants**: Support for product variants (sizes, colors, etc.)
4. **Reviews & Ratings**: Product review and rating system
5. **Recommendations**: Product recommendation engine
6. **Image Processing**: Automated image optimization and processing
7. **Bulk Operations**: Support for bulk product imports/exports

This specification provides a solid foundation for developing a standalone product microservice that can replace the current product functionality in the monolithic application.