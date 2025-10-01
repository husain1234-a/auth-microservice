# Microservices with Firebase Authentication

A comprehensive microservices architecture using FastAPI with Firebase authentication across all services.

## Overview

This project implements a complete microservices architecture with Firebase authentication integrated across all services. The architecture includes:

- **Product Service**: Manages products and categories
- **Cart Service**: Handles user shopping carts and wishlists
- **Auth Service**: Authentication and user management
- **API Gateway**: Centralized routing and security
- **Database**: PostgreSQL with isolated databases per service

All services use Firebase authentication for consistent, secure user authentication.

## Features

### Cross-Service Authentication
- **Firebase Authentication** across all microservices
- **Consistent Security** with centralized authentication
- **Token Validation** at service level
- **Session Management** with HTTP-only cookies

### Service Features
- **Product Service**: Product and category management with Cloudflare R2 image storage
- **Cart Service**: Shopping cart and wishlist functionality with dual-write database support
- **Auth Service**: User authentication with Google OAuth and Phone Number authentication
- **API Gateway**: Centralized routing with circuit breaker and rate limiting

### Security Features
- **XSS Protection**: HTTP-only cookies, input sanitization
- **CSRF Protection**: SameSite cookies, CORS configuration
- **Rate Limiting**: Service-level rate limiting
- **Circuit Breaker**: Service failure protection
- **Input Validation**: Pydantic schemas

## Architecture

### Service Structure
```
API Gateway (Port 8000)
├── Product Service (Port 8002)
├── Cart Service (Port 8003)
└── Auth Service (Port 8001)
```

### Database Structure
- **Product Database**: Isolated PostgreSQL database for product data
- **Cart Database**: Isolated PostgreSQL database for cart data
- **Legacy Database**: Shared database for dual-write operations
- **Redis**: Caching and rate limiting

### Authentication Flow
1. User authenticates with Firebase (Google, Phone, Email/Password)
2. Frontend obtains Firebase ID token
3. Token sent in Authorization header to API Gateway
4. Gateway forwards request to appropriate service
5. Service validates Firebase token using Firebase Admin SDK
6. User ID extracted from validated token
7. Business logic executed with authenticated user context

## Firebase Authentication Implementation

### Configuration
All services are configured with Firebase credentials:
- **Firebase Project ID**
- **Service Account Key**
- **Client Email and ID**
- **Token and Auth URIs**

### Token Validation
Services validate Firebase ID tokens using Firebase Admin SDK:
- **verify_id_token()** for Bearer tokens
- **verify_session_cookie()** for web sessions
- **Automatic User ID Extraction**

### Route Protection
All protected routes use Firebase authentication dependency:
```python
@router.get("/protected-route")
async def protected_route(user_id: str = Depends(get_current_user_id)):
    # Route logic here
    pass
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL
- Redis
- Firebase project with Authentication enabled

### Firebase Configuration

1. Create a Firebase project at https://console.firebase.google.com
2. Enable Authentication with desired providers
3. Generate a service account key for Admin SDK
4. Get web app configuration for client SDK

### Environment Setup

#### Product Service
Configure [backend/product_service/.env](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/backend/product_service/.env):
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/product_db

# Firebase
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_CLIENT_CERT_URL=your_client_cert_url

# Cloudflare R2
R2_ENDPOINT_URL=your_r2_endpoint
R2_ACCESS_KEY_ID=your_access_key_id
R2_SECRET_ACCESS_KEY=your_secret_access_key
R2_BUCKET_NAME=your_bucket_name
R2_REGION=auto
R2_PUBLIC_URL=your_public_url
```

#### Cart Service
Configure [backend/cart_service/.env](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/backend/cart_service/.env):
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cart_db

# Firebase
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_CLIENT_CERT_URL=your_client_cert_url

# External Services
PRODUCT_SERVICE_URL=http://localhost:8002
```

#### Auth Service
Configure [backend/auth_service/.env](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/backend/auth_service/.env):
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/auth_db

# Firebase
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_CLIENT_CERT_URL=your_client_cert_url

# Redis
REDIS_URL=redis://localhost:6379/0
```

#### Gateway
Configure [backend/gateway/.env](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/backend/gateway/.env):
```env
# Service URLs
PRODUCT_SERVICE_URL=http://localhost:8002
CART_SERVICE_URL=http://localhost:8003
AUTH_SERVICE_URL=http://localhost:8001
```

### Service Installation

#### Product Service
```bash
cd backend/product_service
pip install -r requirements.txt
uvicorn app.main:app --port 8002
```

#### Cart Service
```bash
cd backend/cart_service
pip install -r requirements.txt
uvicorn app.main:app --port 8003
```

#### Auth Service
```bash
cd backend/auth_service
pip install -r requirements.txt
redis-server  # Start Redis
uvicorn app.main:app --port 8001
```

#### API Gateway
```bash
cd backend/gateway
pip install -r requirements.txt
uvicorn main:app --port 8000
```

### Docker Setup

1. Configure all .env files
2. Start all services:
```bash
docker-compose up --build
```

## API Endpoints

### Product Service
- `GET /api/products` - List products
- `POST /api/products` - Create product (protected)
- `PUT /api/products/{id}` - Update product (protected)
- `DELETE /api/products/{id}` - Delete product (protected)
- `GET /api/categories` - List categories
- `POST /api/categories` - Create category (protected)
- `PUT /api/categories/{id}` - Update category (protected)

### Cart Service
- `GET /api/v1/cart` - Get user's cart (protected)
- `POST /api/v1/cart/add` - Add item to cart (protected)
- `POST /api/v1/cart/remove` - Remove item from cart (protected)
- `GET /api/v1/wishlist` - Get user's wishlist (protected)
- `POST /api/v1/wishlist/add` - Add item to wishlist (protected)

### Auth Service
- `POST /auth/google-login` - Google OAuth login
- `POST /auth/send-otp` - Send phone verification OTP
- `POST /auth/verify-otp` - Verify OTP and create session
- `GET /auth/me` - Get current user info (protected)
- `POST /auth/logout` - Logout and clear session

### API Gateway
- `GET /health` - System health check
- `GET /gateway/stats` - Gateway statistics
- Routes to all services based on path prefix

## Security Considerations

### Firebase Security
- **Server-side Validation**: All tokens validated with Firebase Admin SDK
- **Secure Credential Storage**: Environment variables for sensitive data
- **Token Expiration**: Automatic handling of token expiration
- **Session Revocation**: Support for session cookie revocation

### Service Security
- **HTTP-only Cookies**: Secure session management
- **CORS Protection**: Configured for trusted origins only
- **Rate Limiting**: Per-service rate limiting
- **Circuit Breaker**: Service failure protection
- **Input Validation**: Pydantic schemas for all inputs

### Network Security
- **Internal Communication**: Service-to-service communication
- **Gateway Protection**: Centralized security enforcement
- **Health Checks**: Service monitoring and failure detection

## Testing

### Unit Testing
Each service includes comprehensive unit tests:
```bash
cd backend/product_service
pytest

cd backend/cart_service
pytest

cd backend/auth_service
pytest
```

### Integration Testing
End-to-end testing through API Gateway:
```bash
cd backend/gateway
pytest
```

## Deployment

### Individual Service Deployment
Each service can be deployed independently:
- **Cloud Run**: Google Cloud Run for containerized deployment
- **EC2**: AWS EC2 instances
- **App Engine**: Google App Engine
- **Heroku**: Heroku dynos

### Kubernetes Deployment
Services can be deployed to Kubernetes:
- **Helm Charts**: For service deployment
- **Ingress Controller**: For routing
- **Secrets Management**: For credential storage

### CI/CD Pipeline
Recommended deployment pipeline:
1. Code commit to repository
2. Automated testing
3. Container image build
4. Security scanning
5. Deployment to staging
6. Manual approval for production

## Monitoring and Logging

### Service Monitoring
- **Health Checks**: Built-in health endpoints
- **Metrics Collection**: Performance metrics
- **Error Tracking**: Exception monitoring
- **Log Aggregation**: Centralized logging

### Firebase Monitoring
- **Authentication Logs**: User login/logout tracking
- **Token Usage**: Token validation metrics
- **Security Events**: Suspicious activity detection

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License

## Additional Documentation

- [Firebase Authentication Implementation Summary](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/FINAL_FIREBASE_AUTH_IMPLEMENTATION_SUMMARY.md)
- [Microservice Architecture Fixes](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/MICROSERVICE_ARCHITECTURE_FIXES_PRODUCTION.md)
- [Database Migration Scripts](file:///c%3A/Users/husain.burhanpurwala/Downloads/auth-microservice/database/migrations/remove_foreign_keys.sql)