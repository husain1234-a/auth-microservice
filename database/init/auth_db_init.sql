-- Auth Service Database Initialization Script
-- This script creates the necessary tables for the Auth Service

-- Enable UUID extension for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table - core user information
CREATE TABLE users (
    uid VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    display_name VARCHAR(255) NOT NULL,
    photo_url TEXT,
    role VARCHAR(50) DEFAULT 'user' CHECK (
        role IN ('user', 'admin', 'owner', 'delivery_moderator')
    ),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- User sessions table for session management
CREATE TABLE user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users (uid) ON DELETE CASCADE,
    device_info TEXT,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        last_accessed_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- User profiles table for extended user information
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL REFERENCES users (uid) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    address_line1 TEXT,
    address_line2 TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users (email);

CREATE INDEX idx_users_active ON users (is_active);

CREATE INDEX idx_user_sessions_user_id ON user_sessions (user_id);

CREATE INDEX idx_user_sessions_expires_at ON user_sessions (expires_at);

CREATE INDEX idx_user_profiles_user_id ON user_profiles (user_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (for development/testing)
INSERT INTO
    users (
        uid,
        email,
        display_name,
        role
    )
VALUES (
        'admin-001',
        'admin@grofast.com',
        'System Administrator',
        'admin'
    ) ON CONFLICT (uid) DO NOTHING;