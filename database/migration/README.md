# Database Migration Scripts

This directory contains scripts for migrating from the monolithic database to separate service databases.

## Migration Strategy

The migration follows a phased approach:

1. **Extract Data**: Extract service-specific data from the monolithic database
2. **Validate Data**: Ensure data integrity and consistency during migration
3. **Load Data**: Load data into the new service-specific databases
4. **Rollback**: Provide rollback capabilities for each migration step

## Scripts Overview

- `extract_auth_data.sql` - Extract user and auth-related data
- `extract_product_data.sql` - Extract product and category data
- `extract_cart_data.sql` - Extract cart and wishlist data
- `extract_promotion_data.sql` - Extract promo code data
- `validate_migration.py` - Validate data consistency after migration
- `rollback_migration.py` - Rollback migration steps
- `migrate_data.py` - Main migration orchestrator

## Usage

1. Run the main migration script:
   ```bash
   python database/migration/migrate_data.py
   ```

2. Validate the migration:
   ```bash
   python database/migration/validate_migration.py
   ```

3. If needed, rollback:
   ```bash
   python database/migration/rollback_migration.py
   ```

## Requirements

- PostgreSQL client (psql)
- Python 3.8+
- psycopg2-binary
- asyncpg