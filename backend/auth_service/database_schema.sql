-- Auth Microservice Database Schema
-- This schema is designed for isolated auth service database

-- Users table (managed by auth service)
CREATE TABLE users (
    uid varchar(255) NOT NULL,
    email varchar(255) UNIQUE,
    phone_number varchar(20) UNIQUE,
    display_name varchar(255),
    photo_url text,
    role varchar(50) DEFAULT 'customer'::character varying,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (uid)
);

-- Indexes for better performance
CREATE INDEX ix_users_uid ON users USING btree (uid);

CREATE INDEX ix_users_email ON users USING btree (email);

CREATE INDEX ix_users_phone_number ON users USING btree (phone_number);

-- Grant privileges to poc_user
GRANT ALL PRIVILEGES ON TABLE users TO poc_user;

-- Grant usage on the schema
GRANT USAGE ON SCHEMA public TO poc_user;