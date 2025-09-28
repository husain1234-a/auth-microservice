# Getting Started with Local PostgreSQL Setup

This guide will help you set up the microservice databases on your local machine without Docker.

## Prerequisites

1. **PostgreSQL Installation**
   - Download from: https://www.postgresql.org/download/
   - Make sure `psql` command is available in your PATH
   - Remember your PostgreSQL superuser password

2. **Python** (for testing scripts)
   - Python 3.7 or higher
   - pip package manager

## Quick Setup (5 minutes)

### Step 1: Install Python Dependencies
```bash
python database/install_dependencies.py
```

### Step 2: Create Databases
**Windows:**
```cmd
database\start_databases.bat
```

**Linux/Mac:**
```bash
chmod +x database/start_databases.sh
./database/start_databases.sh
```

### Step 3: Verify Setup
```bash
python database/verify_setup.py
```

## What Gets Created

The setup script creates:

- **5 separate databases** (auth_db, product_db, cart_db, promotion_db, poc)
- **5 database users** with appropriate permissions
- **Complete table schemas** with indexes and triggers
- **Sample data** for testing

## Database Details

| Service | Database | User | Port | Connection String |
|---------|----------|------|------|-------------------|
| Auth | auth_db | auth_user | 5432 | postgresql://auth_user:auth_pass123@localhost:5432/auth_db |
| Product | product_db | product_user | 5432 | postgresql://product_user:product_pass123@localhost:5432/product_db |
| Cart | cart_db | cart_user | 5432 | postgresql://cart_user:cart_pass123@localhost:5432/cart_db |
| Promotion | promotion_db | promotion_user | 5432 | postgresql://promotion_user:promotion_pass123@localhost:5432/promotion_db |
| Legacy | poc | poc_user | 5432 | postgresql://poc_user:admin123@localhost:5432/poc |

## Testing Your Setup

### 1. Basic Connection Test
```bash
python database/verify_setup.py
```

### 2. Advanced Connection Test (requires asyncpg)
```bash
python database/test_connections.py
```

### 3. Manual Database Access
```bash
# Connect to auth database
psql -h localhost -U auth_user -d auth_db

# List tables
\dt

# Check a table
SELECT * FROM users LIMIT 5;
```

## Using in Your Services

### Environment Variables
Use the provided configuration file:

```bash
# Copy the local config
cp database/local_config.env .env.local
```

### Python Example
```python
import os
from dotenv import load_dotenv

# Load local database configuration
load_dotenv('database/local_config.env')

# Get database URL for your service
auth_db_url = os.getenv('AUTH_DATABASE_URL')
product_db_url = os.getenv('PRODUCT_DATABASE_URL')
```

### FastAPI/SQLAlchemy Example
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine

# For auth service
engine = create_async_engine(
    "postgresql+asyncpg://auth_user:auth_pass123@localhost:5432/auth_db"
)
```

## Troubleshooting

### PostgreSQL Not Found
```bash
# Check if PostgreSQL is installed
psql --version

# If not found, install PostgreSQL:
# Windows: Download from postgresql.org
# Ubuntu: sudo apt-get install postgresql postgresql-client
# macOS: brew install postgresql
```

### Permission Denied
```bash
# Make sure PostgreSQL service is running
# Windows: Check Services app
# Linux: sudo systemctl start postgresql
# macOS: brew services start postgresql
```

### Database Already Exists
The setup scripts handle existing databases gracefully. If you need to reset:

```sql
-- Connect as superuser and drop databases
DROP DATABASE IF EXISTS auth_db;
DROP DATABASE IF EXISTS product_db;
DROP DATABASE IF EXISTS cart_db;
DROP DATABASE IF EXISTS promotion_db;

-- Drop users
DROP USER IF EXISTS auth_user;
DROP USER IF EXISTS product_user;
DROP USER IF EXISTS cart_user;
DROP USER IF EXISTS promotion_user;
```

### Connection Refused
1. Check if PostgreSQL is running
2. Verify the port (default 5432)
3. Check firewall settings
4. Verify pg_hba.conf allows local connections

## Next Steps

1. **Update Service Configurations**: Use the new database URLs in your services
2. **Test Service Connections**: Make sure each service can connect to its database
3. **Run Migrations**: If you have existing data, plan your migration strategy
4. **Monitor Performance**: Set up monitoring for the new database structure

## Security Notes

- Change default passwords in production
- Use environment variables for credentials
- Consider using connection pooling
- Set up proper backup strategies
- Monitor database access logs

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify PostgreSQL installation and service status
3. Run the verification scripts for detailed error messages
4. Check PostgreSQL logs for connection issues