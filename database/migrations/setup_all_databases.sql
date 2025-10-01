-- Setup script for all microservice databases
-- This script creates the poc_user and sets up permissions for all databases

-- Connect to PostgreSQL as superuser (postgres) and run these commands:

-- Create the poc_user if it doesn't exist
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'poc_user') THEN

      CREATE ROLE poc_user LOGIN PASSWORD 'admin123';
   END IF;
END
$do$;

-- Grant necessary privileges to poc_user for all databases

-- For auth_db
\c auth_db;

GRANT ALL PRIVILEGES ON SCHEMA public TO poc_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO poc_user;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO poc_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO poc_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO poc_user;

-- For product_db
\c product_db;

GRANT ALL PRIVILEGES ON SCHEMA public TO poc_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO poc_user;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO poc_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO poc_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO poc_user;

-- For cart_db
\c cart_db;

GRANT ALL PRIVILEGES ON SCHEMA public TO poc_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO poc_user;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO poc_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO poc_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO poc_user;

-- For promotion_db
\c promotion_db;

GRANT ALL PRIVILEGES ON SCHEMA public TO poc_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO poc_user;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO poc_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO poc_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON SEQUENCES TO poc_user;

-- Verify users and permissions
\du+