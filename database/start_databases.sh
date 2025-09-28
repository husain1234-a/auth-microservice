#!/bin/bash

# Database Setup Script for Microservices Migration (Local PostgreSQL)
# This script creates databases and users in a local PostgreSQL installation

echo "🚀 Setting up microservice databases (Local PostgreSQL)..."
echo "========================================================"

# Check if PostgreSQL is installed and accessible
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed or not in PATH"
    echo "Please install PostgreSQL:"
    echo "  - Ubuntu/Debian: sudo apt-get install postgresql postgresql-client"
    echo "  - macOS: brew install postgresql"
    echo "  - CentOS/RHEL: sudo yum install postgresql postgresql-server"
    exit 1
fi

echo "✅ PostgreSQL found"

# Get PostgreSQL superuser credentials
read -p "Enter PostgreSQL superuser (default: postgres): " POSTGRES_USER
POSTGRES_USER=${POSTGRES_USER:-postgres}

echo ""
echo "Creating databases and users..."
echo "=============================="

# Create databases and users using psql
echo "Creating Auth Database..."
psql -U "$POSTGRES_USER" -c "CREATE DATABASE auth_db;" 2>/dev/null || true
psql -U "$POSTGRES_USER" -c "CREATE USER auth_user WITH PASSWORD 'auth_pass123';" 2>/dev/null || true
psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;" 2>/dev/null || true
psql -U "$POSTGRES_USER" -d auth_db -f "database/init/auth_db_init.sql" 2>/dev/null || true

echo "Creating Product Database..."
psql -U "$POSTGRES_USER" -c "CREATE DATABASE product_db;" 2>/dev/null || true
psql -U "$POSTGRES_USER" -c "CREATE USER product_user WITH PASSWORD 'product_pass123';" 2>/dev/null || true
psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE product_db TO product_user;" 2>/dev/null || true
psql -U "$POSTGRES_USER" -d product_db -f "database/init/product_db_init.sql" 2>/dev/null || true

echo "Creating Cart Database..."
psql -U "$POSTGRES_USER" -c "CREATE DATABASE cart_db;" 2>/dev/null || true
psql -U "$POSTGRES_USER" -c "CREATE USER cart_user WITH PASSWORD 'cart_pass123';" 2>/dev/null || true
psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE cart_db TO cart_user;" 2>/dev/null || true
psql -U "$POSTGRES_USER" -d cart_db -f "database/init/cart_db_init.sql" 2>/dev/null || true

echo "Creating Promotion Database..."
psql -U "$POSTGRES_USER" -c "CREATE DATABASE promotion_db;" 2>/dev/null || true
psql -U "$POSTGRES_USER" -c "CREATE USER promotion_user WITH PASSWORD 'promotion_pass123';" 2>/dev/null || true
psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE promotion_db TO promotion_user;" 2>/dev/null || true
psql -U "$POSTGRES_USER" -d promotion_db -f "database/init/promotion_db_init.sql" 2>/dev/null || true

echo "Creating Legacy Database (if not exists)..."
psql -U "$POSTGRES_USER" -c "CREATE DATABASE poc;" 2>/dev/null || true
psql -U "$POSTGRES_USER" -c "CREATE USER poc_user WITH PASSWORD 'admin123';" 2>/dev/null || true
psql -U "$POSTGRES_USER" -c "GRANT ALL PRIVILEGES ON DATABASE poc TO poc_user;" 2>/dev/null || true

echo ""
echo "🔗 Database Connection Information:"
echo "=================================="
echo "Auth DB:      postgresql://auth_user:auth_pass123@localhost:5432/auth_db"
echo "Product DB:   postgresql://product_user:product_pass123@localhost:5432/product_db"
echo "Cart DB:      postgresql://cart_user:cart_pass123@localhost:5432/cart_db"
echo "Promotion DB: postgresql://promotion_user:promotion_pass123@localhost:5432/promotion_db"
echo "Legacy DB:    postgresql://poc_user:admin123@localhost:5432/poc"

echo ""
echo "✅ All databases created and initialized!"
echo ""
echo "💡 Next steps:"
echo "   1. Test connections: python database/test_connections.py"
echo "   2. Update service configurations to use localhost:5432"
echo "   3. Start your services with the new database URLs"