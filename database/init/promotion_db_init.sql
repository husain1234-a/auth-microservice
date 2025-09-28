-- Promotion Service Database Initialization Script
-- This script creates the necessary tables for the Promotion Service

-- Promo codes table
CREATE TABLE promo_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('percentage', 'fixed_amount', 'free_shipping')),
    discount_value DECIMAL(10,2) NOT NULL CHECK (discount_value >= 0),
    minimum_order_value DECIMAL(10,2) DEFAULT 0 CHECK (minimum_order_value >= 0),
    maximum_discount_amount DECIMAL(10,2), -- Cap for percentage discounts
    max_uses INTEGER, -- NULL for unlimited uses
    max_uses_per_user INTEGER DEFAULT 1,
    used_count INTEGER DEFAULT 0 CHECK (used_count >= 0),
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT true,
    -- Targeting criteria
    applicable_categories INTEGER[], -- Array of category IDs from Product Service
    applicable_products INTEGER[], -- Array of product IDs from Product Service
    applicable_user_roles TEXT[], -- Array of user roles from Auth Service
    minimum_user_age_days INTEGER, -- Minimum account age in days
    -- Usage restrictions
    first_time_users_only BOOLEAN DEFAULT false,
    stackable BOOLEAN DEFAULT false, -- Can be combined with other promos
    auto_apply BOOLEAN DEFAULT false, -- Automatically apply if conditions met
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255), -- Admin user ID who created the promo
    CHECK (valid_from < valid_until)
);

-- Promo code usage tracking
CREATE TABLE promo_usage (
    id SERIAL PRIMARY KEY,
    promo_code_id INTEGER NOT NULL REFERENCES promo_codes (id) ON DELETE CASCADE,
    user_id_ref VARCHAR(255) NOT NULL, -- Reference to Auth Service user
    cart_id_ref INTEGER, -- Reference to Cart Service cart
    order_id_ref VARCHAR(255), -- Reference to Order Service order (when implemented)
    discount_amount DECIMAL(10, 2) NOT NULL CHECK (discount_amount >= 0),
    original_amount DECIMAL(10, 2) NOT NULL CHECK (original_amount >= 0),
    final_amount DECIMAL(10, 2) NOT NULL CHECK (final_amount >= 0),
    usage_context JSONB, -- Additional context about the usage
    applied_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        status VARCHAR(20) DEFAULT 'applied' CHECK (
            status IN (
                'applied',
                'refunded',
                'cancelled'
            )
        )
);

-- Promotion campaigns table (for managing multiple related promos)
CREATE TABLE promotion_campaigns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    campaign_type VARCHAR(50) NOT NULL, -- 'seasonal', 'flash_sale', 'loyalty', etc.
    start_date TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        end_date TIMESTAMP
    WITH
        TIME ZONE NOT NULL,
        budget DECIMAL(12, 2), -- Total budget for the campaign
        spent_amount DECIMAL(12, 2) DEFAULT 0 CHECK (spent_amount >= 0),
        target_audience JSONB, -- Targeting criteria
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        created_by VARCHAR(255),
        CHECK (start_date < end_date)
);

-- Link promo codes to campaigns
CREATE TABLE campaign_promo_codes (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES promotion_campaigns (id) ON DELETE CASCADE,
    promo_code_id INTEGER NOT NULL REFERENCES promo_codes (id) ON DELETE CASCADE,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        UNIQUE (campaign_id, promo_code_id)
);

-- User promo eligibility cache (for performance)
CREATE TABLE user_promo_eligibility (
    id SERIAL PRIMARY KEY,
    user_id_ref VARCHAR(255) NOT NULL,
    promo_code_id INTEGER NOT NULL REFERENCES promo_codes (id) ON DELETE CASCADE,
    is_eligible BOOLEAN NOT NULL,
    eligibility_reason TEXT,
    checked_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        expires_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT(NOW() + INTERVAL '1 hour'),
        UNIQUE (user_id_ref, promo_code_id)
);

-- Promo code analytics and metrics
CREATE TABLE promo_analytics (
    id SERIAL PRIMARY KEY,
    promo_code_id INTEGER NOT NULL REFERENCES promo_codes (id) ON DELETE CASCADE,
    date DATE NOT NULL,
    views INTEGER DEFAULT 0, -- How many times promo was viewed
    attempts INTEGER DEFAULT 0, -- How many times promo was attempted
    successful_uses INTEGER DEFAULT 0, -- How many times promo was successfully applied
    total_discount_given DECIMAL(12, 2) DEFAULT 0,
    total_revenue_generated DECIMAL(12, 2) DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        UNIQUE (promo_code_id, date)
);

-- Automatic promo suggestions (for recommendation engine)
CREATE TABLE promo_suggestions (
    id SERIAL PRIMARY KEY,
    user_id_ref VARCHAR(255) NOT NULL,
    promo_code_id INTEGER NOT NULL REFERENCES promo_codes (id) ON DELETE CASCADE,
    suggestion_reason VARCHAR(100), -- 'cart_value', 'user_behavior', 'seasonal', etc.
    confidence_score DECIMAL(3, 2) CHECK (
        confidence_score >= 0
        AND confidence_score <= 1
    ),
    suggested_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        expires_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT(NOW() + INTERVAL '24 hours'),
        is_shown BOOLEAN DEFAULT false,
        is_clicked BOOLEAN DEFAULT false,
        is_used BOOLEAN DEFAULT false
);

-- Indexes for performance
CREATE INDEX idx_promo_codes_code ON promo_codes (code);

CREATE INDEX idx_promo_codes_active ON promo_codes (is_active);

CREATE INDEX idx_promo_codes_valid_dates ON promo_codes (valid_from, valid_until);

CREATE INDEX idx_promo_codes_auto_apply ON promo_codes (auto_apply)
WHERE
    auto_apply = true;

CREATE INDEX idx_promo_usage_promo_code_id ON promo_usage (promo_code_id);

CREATE INDEX idx_promo_usage_user_id_ref ON promo_usage (user_id_ref);

CREATE INDEX idx_promo_usage_applied_at ON promo_usage (applied_at);

CREATE INDEX idx_promotion_campaigns_active ON promotion_campaigns (is_active);

CREATE INDEX idx_promotion_campaigns_dates ON promotion_campaigns (start_date, end_date);

CREATE INDEX idx_user_promo_eligibility_user_id ON user_promo_eligibility (user_id_ref);

CREATE INDEX idx_user_promo_eligibility_expires_at ON user_promo_eligibility (expires_at);

CREATE INDEX idx_promo_analytics_promo_code_date ON promo_analytics (promo_code_id, date);

CREATE INDEX idx_promo_suggestions_user_id ON promo_suggestions (user_id_ref);

CREATE INDEX idx_promo_suggestions_expires_at ON promo_suggestions (expires_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_promo_codes_updated_at BEFORE UPDATE ON promo_codes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_promotion_campaigns_updated_at BEFORE UPDATE ON promotion_campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update promo code usage count
CREATE OR REPLACE FUNCTION update_promo_usage_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE promo_codes 
        SET used_count = used_count + 1,
            updated_at = NOW()
        WHERE id = NEW.promo_code_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE promo_codes 
        SET used_count = GREATEST(used_count - 1, 0),
            updated_at = NOW()
        WHERE id = OLD.promo_code_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Triggers to automatically update usage count
CREATE TRIGGER update_promo_usage_count_on_insert AFTER INSERT ON promo_usage
    FOR EACH ROW EXECUTE FUNCTION update_promo_usage_count();

CREATE TRIGGER update_promo_usage_count_on_delete AFTER DELETE ON promo_usage
    FOR EACH ROW EXECUTE FUNCTION update_promo_usage_count();

-- Function to clean up expired eligibility cache
CREATE OR REPLACE FUNCTION cleanup_expired_eligibility()
RETURNS void AS $$
BEGIN
    DELETE FROM user_promo_eligibility WHERE expires_at < NOW();
    DELETE FROM promo_suggestions WHERE expires_at < NOW();
END;
$$ language 'plpgsql';

-- Insert sample promo codes for testing
INSERT INTO
    promo_codes (
        code,
        name,
        description,
        discount_type,
        discount_value,
        minimum_order_value,
        max_uses,
        valid_from,
        valid_until
    )
VALUES (
        'WELCOME10',
        'Welcome Discount',
        '10% off for new users',
        'percentage',
        10.00,
        50.00,
        NULL,
        NOW(),
        NOW() + INTERVAL '1 year'
    ),
    (
        'SAVE20',
        'Save $20',
        '$20 off orders over $100',
        'fixed_amount',
        20.00,
        100.00,
        1000,
        NOW(),
        NOW() + INTERVAL '6 months'
    ),
    (
        'FREESHIP',
        'Free Shipping',
        'Free shipping on all orders',
        'free_shipping',
        0.00,
        25.00,
        NULL,
        NOW(),
        NOW() + INTERVAL '3 months'
    ) ON CONFLICT (code) DO NOTHING;