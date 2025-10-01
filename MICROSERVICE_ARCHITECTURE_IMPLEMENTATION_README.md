# Microservice Architecture Implementation Guide

This document provides instructions for implementing the microservice architecture improvements to remove foreign key constraints and improve service independence.

## Overview

This implementation addresses the following key issues:
1. Removal of foreign key constraints between microservices
2. Implementation of secure JWT-based authentication
3. Reliable service-to-service communication with circuit breakers
4. Data consistency mechanisms through event-driven architecture
5. Reliability patterns including health checks and rate limiting

## Implementation Steps

### 1. Database Schema Changes

Run the migration script:
```sql
-- database/migrations/remove_foreign_keys.sql
-- Product Service Migrations
-- Remove foreign key constraint but keep the column
ALTER TABLE products DROP CONSTRAINT IF EXISTS products_category_id_fkey;
ALTER TABLE products ALTER COLUMN category_id DROP NOT NULL;

-- Add category_name column for denormalization
ALTER TABLE products ADD COLUMN IF NOT EXISTS category_name VARCHAR(100);

-- Populate category_name with existing data
UPDATE products 
SET category_name = (SELECT name FROM categories WHERE categories.id = products.category_id)
WHERE category_id IS NOT NULL AND category_name IS NULL;

-- Cart Service Migrations
-- Remove all foreign key constraints:
ALTER TABLE carts DROP CONSTRAINT IF EXISTS carts_user_id_fkey;
ALTER TABLE cart_items DROP CONSTRAINT IF EXISTS cart_items_cart_id_fkey;
ALTER TABLE wishlists DROP CONSTRAINT IF EXISTS wishlists_user_id_fkey;
ALTER TABLE wishlist_items DROP CONSTRAINT IF EXISTS wishlist_items_wishlist_id_fkey;
ALTER TABLE cart_promo_codes DROP CONSTRAINT IF EXISTS cart_promo_codes_cart_id_fkey;
ALTER TABLE cart_promo_codes DROP CONSTRAINT IF EXISTS cart_promo_codes_promo_code_id_fkey;
```

### 2. Model Updates

#### Product Service Models
- `backend/product_service/app/models/product.py`: Removed ForeignKey constraint and relationship
- `backend/product_service/app/models/category.py`: Removed relationship to products

#### Cart Service Models
- `backend/cart_service/app/models/cart.py`: Removed all ForeignKey constraints and relationships
- `backend/cart_service/app/models/user.py`: Deleted (data now comes from Auth Service)

### 3. Service Communication Improvements

#### Circuit Breaker Pattern
Implemented in `backend/cart_service/app/utils/circuit_breaker.py`:
- Prevents cascade failures when services are unavailable
- Configurable failure thresholds and recovery timeouts

#### Caching with TTL
Implemented in `backend/cart_service/app/services/product_service.py`:
- In-memory caching with 5-minute TTL
- Automatic cache invalidation

#### Event-Driven Architecture
- Product Service publishes events when data changes (`backend/product_service/app/services/event_publisher.py`)
- Cart Service handles events to maintain data consistency (`backend/cart_service/app/routes/internal.py`)

### 4. Security Enhancements

#### JWT Validation
- Added JWT configuration to `backend/cart_service/app/core/config.py`
- Implemented JWT validation in `backend/cart_service/app/core/security.py`
- Route handlers now use proper FastAPI dependency injection for authentication

### 5. Reliability Patterns

#### Health Checks
- Internal health check endpoints at `/internal/health`
- Service-to-service health monitoring

#### Rate Limiting
- Implemented in `backend/cart_service/app/middleware/rate_limiter.py`
- Protects internal endpoints from abuse

#### Dead Letter Queue
- Event processing with retry logic in `backend/cart_service/app/services/event_processor.py`
- Failed events moved to dead letter queue for manual handling

## File Structure Changes

```
backend/
├── product_service/
│   ├── app/
│   │   ├── models/
│   │   │   ├── product.py (updated)
│   │   │   └── category.py (updated)
│   │   ├── services/
│   │   │   ├── product_service.py (updated)
│   │   │   ├── category_service.py (updated)
│   │   │   └── event_publisher.py (new)
│   │   └── core/
│   │       └── config.py (updated)
│   └── ...
└── cart_service/
    ├── app/
    │   ├── models/
    │   │   ├── cart.py (updated)
    │   │   └── user.py (deleted)
    │   ├── services/
    │   │   ├── product_service.py (updated)
    │   │   └── event_processor.py (new)
    │   ├── routes/
    │   │   ├── api.py (existing)
    │   │   └── internal.py (new)
    │   ├── utils/
    │   │   └── circuit_breaker.py (new)
    │   ├── middleware/
    │   │   └── rate_limiter.py (new)
    │   ├── core/
    │   │   └── config.py (already had JWT config)
    │   └── main.py (updated)
    └── ...
```

## Testing the Implementation

### 1. Start the Services
```bash
# Start Product Service
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Start Cart Service
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### 2. Test Health Endpoints
```bash
# Test Product Service Health
curl http://localhost:8002/health

# Test Cart Service Health
curl http://localhost:8003/health

# Test Cart Service Internal Health
curl http://localhost:8003/internal/health
```

### 3. Test Service Communication
```bash
# Test Product Service API
curl http://localhost:8002/api/products

# Test Cart Service API (requires JWT token)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8003/api/v1/cart
```

### 4. Test Event Handling
```bash
# Send test event to Cart Service
curl -X POST http://localhost:8003/internal/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "category.updated",
    "payload": {
      "category_id": 1,
      "name": "Updated Category"
    },
    "timestamp": 1234567890
  }'
```

## Rollback Plan

If issues are encountered:

1. Restore the database from backup
2. Revert model files to previous versions
3. Remove new files (event_publisher.py, circuit_breaker.py, etc.)
4. Restore main.py to previous version

## Monitoring and Maintenance

1. Monitor circuit breaker states in logs
2. Check dead letter queue for failed events
3. Monitor cache hit/miss ratios
4. Watch for rate limiting events
5. Verify event processing success rates

## Next Steps

1. Implement Redis-based distributed caching for production
2. Add message queue (Kafka/RabbitMQ) for event handling
3. Implement distributed tracing
4. Add comprehensive unit and integration tests
5. Set up monitoring and alerting