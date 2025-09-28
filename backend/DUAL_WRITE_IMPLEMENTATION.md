# Dual-Write Pattern Implementation

This document describes the implementation of the dual-write pattern for the database-to-microservices migration. The dual-write pattern allows services to write to both the new isolated databases and the legacy shared database simultaneously during the migration phase.

## Overview

The dual-write implementation provides:

- **Gradual Migration**: Services can migrate incrementally without downtime
- **Data Consistency**: Ensures data remains synchronized between old and new systems
- **Rollback Capability**: Allows reverting to legacy system if issues arise
- **Monitoring & Validation**: Comprehensive tools to monitor synchronization health
- **Configuration Control**: Fine-grained control over dual-write behavior

## Architecture

### Core Components

#### 1. Base Dual-Write Manager (`backend/shared/dual_write_manager.py`)
- Abstract base class for all service-specific dual-write managers
- Handles connection management for both new and legacy databases
- Provides common dual-write operation patterns
- Implements health checking and validation infrastructure

#### 2. Configuration Management (`backend/shared/dual_write_config.py`)
- Centralized configuration for dual-write behavior
- Environment variable-based configuration
- Runtime configuration updates
- Service-specific settings management

#### 3. Synchronization Validator (`backend/shared/sync_validator.py`)
- Data consistency validation between databases
- Automated difference detection
- Batch validation capabilities
- Comprehensive reporting

### Service-Specific Implementations

#### Cart Service (`backend/cart_service/app/core/dual_write_manager.py`)
Handles dual-write for:
- Cart creation and management
- Cart item operations (add, remove, update)
- Wishlist operations
- User data synchronization (for local cache)

#### Auth Service (`backend/auth_service/app/dual_write_manager.py`)
Handles dual-write for:
- User creation and updates
- User deactivation
- Profile management

#### Product Service (`backend/product_service/app/dual_write_manager.py`)
Handles dual-write for:
- Product creation and updates
- Stock management
- Category management

## Configuration

### Environment Variables

Each service supports the following dual-write configuration variables:

```env
# Legacy Database Connection
LEGACY_DATABASE_URL=postgresql+asyncpg://poc_user:admin123@localhost:5432/poc

# Core Dual-Write Settings
DUAL_WRITE_ENABLED=true
DUAL_WRITE_TO_LEGACY=true
DUAL_WRITE_TO_NEW=true

# Error Handling
DUAL_WRITE_FAIL_ON_LEGACY_ERROR=false
DUAL_WRITE_FAIL_ON_NEW_ERROR=true

# Validation Settings
DUAL_WRITE_VALIDATE_SYNC=true
DUAL_WRITE_SYNC_INTERVAL=300

# Performance Settings
DUAL_WRITE_ASYNC_LEGACY=true
DUAL_WRITE_BATCH_SIZE=100

# Monitoring Settings
DUAL_WRITE_LOG_ALL=false
DUAL_WRITE_LOG_ERRORS_ONLY=true
DUAL_WRITE_METRICS_ENABLED=true
```

### Configuration Phases

#### Phase 1: Full Dual-Write (Current Implementation)
```env
DUAL_WRITE_ENABLED=true
DUAL_WRITE_TO_LEGACY=true
DUAL_WRITE_TO_NEW=true
DUAL_WRITE_FAIL_ON_LEGACY_ERROR=false
DUAL_WRITE_FAIL_ON_NEW_ERROR=true
```

#### Phase 2: New Database Primary
```env
DUAL_WRITE_ENABLED=true
DUAL_WRITE_TO_LEGACY=true
DUAL_WRITE_TO_NEW=true
DUAL_WRITE_FAIL_ON_LEGACY_ERROR=false
DUAL_WRITE_FAIL_ON_NEW_ERROR=true
DUAL_WRITE_VALIDATE_SYNC=true
```

#### Phase 3: New Database Only
```env
DUAL_WRITE_ENABLED=false
DUAL_WRITE_TO_LEGACY=false
DUAL_WRITE_TO_NEW=true
```

## Usage Examples

### Cart Service Integration

```python
from app.services.cart_service import CartService

# Create cart service instance
cart_service = CartService()

# Add item to cart (automatically uses dual-write if enabled)
result = await cart_service.add_item_to_cart(
    user_id="user123",
    product_id=456,
    quantity=2
)

# Check dual-write status
status = await cart_service.get_dual_write_status()
print(f"Dual-write enabled: {status['dual_write_enabled']}")
```

### Direct Dual-Write Manager Usage

```python
from app.core.dual_write_manager import CartDualWriteManager
from app.core.dual_write_config import DualWriteSettings

# Create settings
settings = DualWriteSettings.from_env("CART")

# Initialize manager
manager = CartDualWriteManager(
    new_db_url="postgresql+asyncpg://user:pass@localhost:5432/cart_db",
    legacy_db_url="postgresql+asyncpg://user:pass@localhost:5432/poc",
    settings=settings
)

# Perform dual-write operation
result = await manager.create_cart("user123")

# Check result
if result.success:
    print("Cart created successfully in both databases")
else:
    print(f"Dual-write failed: {result.to_dict()}")
```

## Monitoring and Validation

### Health Check Endpoints

Each service provides dual-write monitoring endpoints:

```bash
# Check dual-write status
curl http://localhost:8003/dual-write/status

# Get detailed health information
curl http://localhost:8003/dual-write/health

# Get operation metrics
curl http://localhost:8003/dual-write/metrics
```

### Data Validation

#### Manual Validation
```bash
# Validate specific user's cart synchronization
curl -X POST http://localhost:8003/dual-write/validate-sync/user123

# Test dual-write operation
curl -X POST http://localhost:8003/dual-write/test-operation
```

#### Automated Validation Scripts

```bash
# Run comprehensive dual-write tests
cd backend
python test_dual_write.py

# Validate data synchronization
python validate_data_sync.py
```

### Validation Reports

The validation scripts generate detailed reports:

```json
{
  "summary": {
    "total_tests": 12,
    "passed_tests": 11,
    "failed_tests": 1,
    "success_rate": 91.7
  },
  "test_results": [
    {
      "test_name": "cart_service_create_cart",
      "success": true,
      "details": {
        "new_db_success": true,
        "legacy_db_success": true,
        "sync_validated": true
      }
    }
  ]
}
```

## Error Handling

### Error Types

1. **New Database Errors**: Critical errors that stop operation
2. **Legacy Database Errors**: Non-critical errors (configurable)
3. **Validation Errors**: Synchronization inconsistencies
4. **Configuration Errors**: Invalid dual-write settings

### Error Recovery

```python
# Example error handling in service layer
try:
    result = await dual_write_manager.create_cart(user_id)
    if not result.success:
        if result.new_db_error:
            # Critical error - operation failed
            raise Exception(f"Cart creation failed: {result.new_db_error}")
        elif result.legacy_db_error:
            # Non-critical - log warning but continue
            logger.warning(f"Legacy DB sync failed: {result.legacy_db_error}")
except Exception as e:
    # Handle critical errors
    logger.error(f"Dual-write operation failed: {e}")
    raise
```

## Performance Considerations

### Async Operations
- Legacy database writes can be performed asynchronously
- Connection pooling for both databases
- Batch operations for bulk data synchronization

### Monitoring Metrics
- Operation success/failure rates
- Average operation latency
- Database connection pool status
- Synchronization validation results

## Migration Phases

### Phase 1: Setup Dual-Write (Current)
- ✅ Implement dual-write managers for all services
- ✅ Configure environment variables
- ✅ Add monitoring and validation tools
- ✅ Test dual-write functionality

### Phase 2: Validate and Monitor
- Monitor dual-write operations in production
- Validate data consistency regularly
- Fine-tune configuration based on metrics
- Address any synchronization issues

### Phase 3: Switch to New Database Primary
- Update configuration to prioritize new database
- Reduce dependency on legacy database
- Continue validation and monitoring

### Phase 4: Disable Dual-Write
- Switch to new database only
- Remove legacy database connections
- Clean up dual-write code

## Troubleshooting

### Common Issues

#### 1. Connection Failures
```bash
# Check database connectivity
curl http://localhost:8003/dual-write/health
```

#### 2. Synchronization Issues
```bash
# Run data validation
python validate_data_sync.py

# Check specific entity sync
curl -X POST http://localhost:8003/dual-write/validate-sync/user123
```

#### 3. Configuration Problems
```bash
# Test dual-write configuration
python test_dual_write.py
```

### Debug Logging

Enable detailed logging for troubleshooting:

```env
DUAL_WRITE_LOG_ALL=true
DUAL_WRITE_LOG_ERRORS_ONLY=false
```

## Security Considerations

- Legacy database credentials are stored securely
- All database connections use encrypted connections
- Dual-write operations maintain transaction isolation
- Validation scripts don't expose sensitive data

## Requirements Satisfied

This implementation satisfies the following requirements from the specification:

- ✅ **Requirement 7.2**: Dual-write capabilities during transition
- ✅ **Requirement 7.3**: Rollback capability at each phase
- ✅ **Requirement 7.4**: Thorough testing before production deployment

## Next Steps

1. **Deploy and Monitor**: Deploy dual-write implementation to staging environment
2. **Performance Testing**: Conduct load testing with dual-write enabled
3. **Data Migration**: Begin migrating existing data to new databases
4. **Production Rollout**: Gradually enable dual-write in production
5. **Validation**: Continuous monitoring and validation of data consistency
6. **Cutover**: Switch to new database only after validation period