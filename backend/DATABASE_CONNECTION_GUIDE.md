# Database Connection Management for Isolated Databases

This document describes the implementation of database connection management for the microservices migration, where each service now has its own isolated database.

## Overview

As part of the database-to-microservices migration, each service now manages its own database connection with the following improvements:

- **Isolated Databases**: Each service connects to its own dedicated database
- **Connection Pooling**: Optimized connection pools for better performance
- **Health Monitoring**: Comprehensive health checks and monitoring
- **Fault Tolerance**: Proper error handling and connection recovery

## Service Database Mapping

| Service | Database Name | Port | Connection Pool Size |
|---------|---------------|------|---------------------|
| Auth Service | `auth_db` | 5432 | 10 (max 20 overflow) |
| Cart Service | `cart_db` | 5432 | 10 (max 20 overflow) |
| Product Service | `product_db` | 5432 | 10 (max 20 overflow) |

## Configuration

### Environment Variables

Each service now includes the following database configuration variables:

```env
# Database Connection
DATABASE_URL=postgresql+asyncpg://poc_user:admin123@localhost:5432/{service}_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME={service}_db
DATABASE_USER=poc_user
DATABASE_PASSWORD=admin123

# Connection Pool Settings (for future use)
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

### Connection Configuration

Each service uses SQLAlchemy's async engine with the following settings:

- **Pre-ping**: Validates connections before use
- **Echo**: SQL logging enabled in development mode
- **Future**: Uses SQLAlchemy 2.0 style
- **Async**: Full async/await support for non-blocking operations

## Implementation Details

### Database Connection Files

#### Auth Service
- **Config**: `backend/auth_service/config/settings.py`
- **Database**: `backend/auth_service/app/database.py`
- **Monitor**: `backend/auth_service/app/utils/db_monitor.py`

#### Cart Service
- **Config**: `backend/cart_service/app/core/config.py`
- **Database**: `backend/cart_service/app/core/database.py`
- **Monitor**: `backend/cart_service/app/utils/db_monitor.py`

#### Product Service
- **Config**: `backend/product_service/app/core/config.py`
- **Database**: `backend/product_service/app/core/database.py`
- **Monitor**: `backend/product_service/app/utils/db_monitor.py`

### Key Features

#### 1. Async Engine Configuration
```python
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Validates connections before use
)
```

#### 2. Session Management
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()
```

#### 3. Health Checks
```python
async def check_database_health() -> bool:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
```

## Health Check Endpoints

### Basic Health Check
- **Endpoint**: `GET /health`
- **Purpose**: Quick health status including database connectivity
- **Response**:
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "database_name": "auth_db"
  }
}
```

### Detailed Health Check
- **Endpoint**: `GET /health/detailed`
- **Purpose**: Comprehensive health information including pool metrics
- **Response**:
```json
{
  "timestamp": 1234567890.123,
  "service": "auth-service",
  "database_name": "auth_db",
  "overall_status": "healthy",
  "pool_status": {
    "pool_size": 10,
    "checked_in_connections": 8,
    "checked_out_connections": 2,
    "overflow_connections": 0,
    "total_connections": 10
  },
  "operation_tests": {
    "connection_test": true,
    "read_test": true,
    "write_test": true,
    "transaction_test": true
  },
  "database_info": {
    "database_version": "PostgreSQL 14.x",
    "database_name": "auth_db",
    "active_connections": 5
  }
}
```

## Monitoring and Observability

### Database Monitor Class

Each service includes a `DatabaseMonitor` class that provides:

1. **Connection Pool Status**: Real-time pool metrics
2. **Operation Tests**: Validates basic database operations
3. **Database Information**: Server version, connection counts
4. **Comprehensive Health Checks**: Combines all monitoring data

### Logging

All database operations include structured logging:
- Connection establishment/closure
- Health check results
- Error conditions with detailed messages
- Pool status changes

## Testing

### Connection Test Script

Run the database connection test script to verify all services can connect:

```bash
cd backend
python test_db_connections.py
```

This script tests:
- Auth Service connection to `auth_db`
- Cart Service connection to `cart_db`
- Product Service connection to `product_db`

### Manual Testing

Test individual service health checks:

```bash
# Auth Service
curl http://localhost:8001/health
curl http://localhost:8001/health/detailed

# Cart Service
curl http://localhost:8003/health
curl http://localhost:8003/health/detailed

# Product Service
curl http://localhost:8002/health
curl http://localhost:8002/health/detailed
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Verify database server is running
   - Check database name exists
   - Verify credentials in .env file

2. **Connection Issues**
   - Monitor `/health/detailed` endpoint for connection metrics
   - Check for connection leaks in application code
   - Verify database server capacity

3. **Slow Connections**
   - Check network latency to database
   - Monitor database server performance
   - Review query performance

### Monitoring Commands

```bash
# Check pool status
curl http://localhost:8001/health/detailed | jq '.pool_status'

# Monitor database connections
psql -h localhost -U poc_user -d auth_db -c "SELECT * FROM pg_stat_activity WHERE datname = 'auth_db';"
```

## Migration Notes

### Changes Made

1. **Environment Configuration**: Added pool-specific settings
2. **Database Engines**: Updated to use connection pooling
3. **Session Management**: Enhanced error handling and cleanup
4. **Health Checks**: Added comprehensive monitoring
5. **Lifecycle Management**: Proper startup/shutdown handling

### Requirements Satisfied

- ✅ **Requirement 1.1**: Each service has isolated database configuration
- ✅ **Requirement 1.2**: Services only access their own databases
- ✅ **Requirement 1.5**: Proper connection pool management implemented

This implementation provides a robust foundation for the microservices architecture with proper database isolation, monitoring, and fault tolerance.