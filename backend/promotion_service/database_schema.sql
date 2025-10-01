-- Promotion Microservice Database Schema
-- This schema is designed for isolated promotion service database

-- Promo codes table
CREATE TABLE promo_codes (
    id SERIAL NOT NULL,
    code varchar(50) NOT NULL UNIQUE,
    discount_type varchar(20) NOT NULL, -- 'percentage' or 'fixed_amount'
    discount_value double precision NOT NULL,
    minimum_order_value double precision DEFAULT 0,
    max_uses integer,
    used_count integer DEFAULT 0,
    valid_from timestamp with time zone,
    valid_until timestamp with time zone,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    PRIMARY KEY (id),
    CONSTRAINT promo_codes_discount_value_check CHECK (discount_value > 0),
    CONSTRAINT promo_codes_minimum_order_value_check CHECK (minimum_order_value >= 0),
    CONSTRAINT promo_codes_max_uses_check CHECK (max_uses > 0),
    CONSTRAINT promo_codes_used_count_check CHECK (used_count >= 0)
);

-- User promo code usage tracking
CREATE TABLE user_promo_usage (
    id SERIAL NOT NULL,
    user_id varchar(255) NOT NULL,
    promo_code_id integer NOT NULL,
    used_at timestamp with time zone DEFAULT now(),
    order_id varchar(255),
    PRIMARY KEY (id)
);

-- Indexes for better performance
CREATE INDEX ix_promo_codes_code ON promo_codes (code);

CREATE INDEX ix_promo_codes_active ON promo_codes (is_active);

CREATE INDEX ix_user_promo_usage_user_id ON user_promo_usage (user_id);

CREATE INDEX ix_user_promo_usage_promo_code_id ON user_promo_usage (promo_code_id);

-- Grant privileges to poc_user
GRANT ALL PRIVILEGES ON TABLE promo_codes TO poc_user;

GRANT ALL PRIVILEGES ON TABLE user_promo_usage TO poc_user;

-- Grant usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO poc_user;

-- Grant usage on the schema
GRANT USAGE ON SCHEMA public TO poc_user;