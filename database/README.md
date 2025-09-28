# Database Configuration for Microservices Migration

This directory contains the database initialization scripts and configuration for the microservices migration project.

## Database Architecture

The system has been migrated from a single monolithic PostgreSQL database to separate databases for each service:

### Service Databases

1. **Auth Service Database** (`auth_db`)
   - Port: 5433
   - User: `auth_user`
   - Password: `auth_pass123`
   - Tables: users, user_sessions, user_profiles

2. **Product Service Database** (`product_db`)
   - Port: 5434
   - User: `product_user`
   - Password: `product_pass123`
   - Tables: categories, products, product_inventory, product_images, product_variants

3. **Cart Service Database** (`cart_db`)
   - Port: 5435
   - User: `cart_user`
   - Password: `cart_pass123`
   - Tables: carts, cart_items, wishlists, wishlist_items, cart_view, saved_carts, reference_validation_log

4. **Promotion Service Database** (`promotion_db`)
   - Port: 5436
   - User: `promotion_user`
   - Password: `promotion_pass123`
   - Tables: promo_codes, promo_usage, promotion_campaigns, campaign_promo_codes, user_promo_eligibility, promo_analytics, promo_suggestions

5. **Legacy Database** (`poc`)
   - Port: 5432 (maintained during migration)
   - User: `poc_user`
   - Password: `admin123`
   - Status: Will be decommissioned after migration completion

## Initialization Scripts

Each service has its own initialization script in the `init/` directory:

- `auth_db_init.sql` - Creates auth service tables and indexes
- `product_db_init.sql` - Creates product service tables and indexes
- `cart_db_init.sql` - Creates cart service tables and indexes
- `promotion_db_init.sql` - Creates promotion service tables and indexes

## Key Features

### Cross-Service References
- Services use reference IDs instead of foreign keys
- Reference validation is handled through service communication
- Denormalized data is used for performance optimization

### Data Consistency
- Each service owns its data completely
- Eventual consistency through event-driven patterns
- Validation logs for cross-service references

### Performance Optimizations
- Appropriate indexes for common queries
- Denormalized read models (CQRS pattern)
- Cached data for frequently accessed information

### Audit and Monitoring
- Automatic timestamp updates
- Usage tracking and analytics
- Reference validation logging

## Running the Databases

### Prerequisites

1. **Install PostgreSQL**: Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. **Install Python Dependencies**: Run `python database/install_dependencies.py`

### Setup Databases

To create all databases and users:

**Windows:**
```cmd
database\start_databases.bat
```

**Linux/Mac:**
```bash
chmod +x database/start_databases.sh
./database/start_databases.sh
```

### Manual Setup (Alternative)

If the scripts don't work, you can manually create the databases:

```sql
-- Connect as PostgreSQL superuser
CREATE DATABASE auth_db;
CREATE USER auth_user WITH PASSWORD 'auth_pass123';
GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;

CREATE DATABASE product_db;
CREATE USER product_user WITH PASSWORD 'product_pass123';
GRANT ALL PRIVILEGES ON DATABASE product_db TO product_user;

CREATE DATABASE cart_db;
CREATE USER cart_user WITH PASSWORD 'cart_pass123';
GRANT ALL PRIVILEGES ON DATABASE cart_db TO cart_user;

CREATE DATABASE promotion_db;
CREATE USER promotion_user WITH PASSWORD 'promotion_pass123';
GRANT ALL PRIVILEGES ON DATABASE promotion_db TO promotion_user;

CREATE DATABASE poc;
CREATE USER poc_user WITH PASSWORD 'admin123';
GRANT ALL PRIVILEGES ON DATABASE poc TO poc_user;
```

Then run the initialization scripts:
```bash
psql -U auth_user -d auth_db -f database/init/auth_db_init.sql
psql -U product_user -d product_db -f database/init/product_db_init.sql
psql -U cart_user -d cart_db -f database/init/cart_db_init.sql
psql -U promotion_user -d promotion_db -f database/init/promotion_db_init.sql
```

## Connecting to Databases

### From Services (Local Development)
Services connect using localhost:

- Auth Service: `postgresql+asyncpg://auth_user:auth_pass123@localhost:5432/auth_db`
- Product Service: `postgresql+asyncpg://product_user:product_pass123@localhost:5432/product_db`
- Cart Service: `postgresql+asyncpg://cart_user:cart_pass123@localhost:5432/cart_db`
- Promotion Service: `postgresql+asyncpg://promotion_user:promotion_pass123@localhost:5432/promotion_db`

### Direct Database Access
For direct database access:

```bash
# Auth database
psql -h localhost -U auth_user -d auth_db

# Product database
psql -h localhost -U product_user -d product_db

# Cart database
psql -h localhost -U cart_user -d cart_db

# Promotion database
psql -h localhost -U promotion_user -d promotion_db

# Legacy database
psql -h localhost -U poc_user -d poc
```

### Using Configuration File
Use the provided `database/local_config.env` file in your services:

```python
# Example usage in Python
from dotenv import load_dotenv
import os

load_dotenv('database/local_config.env')
database_url = os.getenv('AUTH_DATABASE_URL')
```

## Migration Strategy

During the migration phase, services maintain connections to both their new dedicated database and the legacy database:

- `DATABASE_URL` - Points to the new service-specific database
- `LEGACY_DATABASE_URL` - Points to the legacy shared database

This dual-write approach allows for gradual migration and rollback capabilities.

## Security Considerations

- Each service has its own database user with limited permissions
- Passwords should be changed in production environments
- Database connections should use SSL in production
- Consider using secrets management for database credentials

## Monitoring and Maintenance

- Monitor database performance and connection pools
- Regular cleanup of expired cache entries
- Analytics data aggregation for reporting
- Backup strategies for each database

## Next Steps

1. Update service configurations to use new database connections
2. Implement dual-write patterns for gradual migration
3. Set up cross-service communication for reference validation
4. Implement event-driven patterns for data synchronization
5. Monitor and validate data consistency during migration