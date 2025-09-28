# Migration Usage Guide

## Quick Start

1. **Setup Environment**
   ```bash
   cd database/migration
   python setup_migration.py
   ```

2. **Check/Create Databases**
   ```bash
   python check_databases.py
   ```

3. **Run Migration**
   ```bash
   python migrate_data.py
   ```

4. **Validate Migration**
   ```bash
   python validate_migration.py
   ```

5. **Rollback (if needed)**
   ```bash
   python rollback_migration.py
   ```

## Prerequisites

- PostgreSQL client tools (psql, pg_dump)
- Python 3.8+
- All databases running and accessible
- Legacy database with existing data

## Migration Process

### Phase 1: Data Extraction
- Extracts user data from monolithic database
- Extracts product and category data
- Extracts cart and wishlist data
- Extracts promotion/promo code data

### Phase 2: Data Transformation
- Converts foreign key relationships to reference IDs
- Creates denormalized snapshots for performance
- Adds new fields required by microservice architecture

### Phase 3: Data Loading
- Loads data into service-specific databases
- Maintains data integrity and consistency
- Creates audit trails and validation logs

### Phase 4: Validation
- Verifies data counts match between source and target
- Validates cross-service reference consistency
- Checks data integrity constraints
- Validates denormalized data accuracy

## Rollback Options

- **Full Rollback**: Restores all databases from backups
- **Data Only**: Clears migrated data, keeps schema
- **Cleanup Only**: Removes migration artifacts

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify database credentials in scripts
   - Ensure databases are running
   - Check network connectivity

2. **Permission Errors**
   - Verify database user permissions
   - Ensure users can create/drop tables
   - Check file system permissions

3. **Data Validation Failures**
   - Review validation logs
   - Check for data inconsistencies
   - Verify reference integrity

### Log Files

Migration creates detailed log files:
- `migration_YYYYMMDD_HHMMSS.log` - Main migration log
- Individual validation results in console output

## Safety Features

- **Automatic Backups**: All databases backed up before migration
- **Validation Checks**: Comprehensive data validation
- **Rollback Capability**: Multiple rollback options
- **Audit Trails**: Detailed logging of all operations