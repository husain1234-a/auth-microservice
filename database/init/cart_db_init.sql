-- Cart Service Database Initialization Script
-- This script creates the necessary tables for the Cart Service

-- Carts table - main shopping cart
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id_ref VARCHAR(255) NOT NULL, -- Reference to Auth Service user
    session_id VARCHAR(255), -- For guest carts
    status VARCHAR(50) DEFAULT 'active' CHECK (
        status IN (
            'active',
            'abandoned',
            'expired'
        )
    ),
    total_items INTEGER DEFAULT 0 CHECK (total_items >= 0),
    total_amount DECIMAL(10, 2) DEFAULT 0 CHECK (total_amount >= 0),
    currency VARCHAR(3) DEFAULT 'INR',
    expires_at TIMESTAMP
    WITH
        TIME ZONE,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- Cart items table
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts (id) ON DELETE CASCADE,
    product_id_ref INTEGER NOT NULL, -- Reference to Product Service
    product_variant_id_ref INTEGER, -- Reference to Product Service variant
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    total_price DECIMAL(10, 2) NOT NULL CHECK (total_price >= 0),
    -- Denormalized data for performance and consistency
    product_name_snapshot VARCHAR(255),
    product_image_snapshot TEXT,
    product_sku_snapshot VARCHAR(100),
    -- Validation tracking
    last_validated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        validation_status VARCHAR(50) DEFAULT 'valid' CHECK (
            validation_status IN ('valid', 'invalid', 'pending')
        ),
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        UNIQUE (
            cart_id,
            product_id_ref,
            product_variant_id_ref
        )
);

-- Wishlists table
CREATE TABLE wishlists (
    id SERIAL PRIMARY KEY,
    user_id_ref VARCHAR(255) NOT NULL, -- Reference to Auth Service user
    name VARCHAR(255) DEFAULT 'My Wishlist',
    description TEXT,
    is_public BOOLEAN DEFAULT false,
    total_items INTEGER DEFAULT 0 CHECK (total_items >= 0),
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- Wishlist items table
CREATE TABLE wishlist_items (
    id SERIAL PRIMARY KEY,
    wishlist_id INTEGER NOT NULL REFERENCES wishlists (id) ON DELETE CASCADE,
    product_id_ref INTEGER NOT NULL, -- Reference to Product Service
    product_variant_id_ref INTEGER, -- Reference to Product Service variant
    -- Denormalized data for performance
    product_name_snapshot VARCHAR(255),
    product_price_snapshot DECIMAL(10, 2),
    product_image_snapshot TEXT,
    -- Validation tracking
    last_validated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        validation_status VARCHAR(50) DEFAULT 'valid' CHECK (
            validation_status IN ('valid', 'invalid', 'pending')
        ),
        notes TEXT,
        priority INTEGER DEFAULT 0,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        UNIQUE (
            wishlist_id,
            product_id_ref,
            product_variant_id_ref
        )
);

-- Cart view for optimized reads (CQRS pattern)
CREATE TABLE cart_view (
    cart_id INTEGER PRIMARY KEY REFERENCES carts (id) ON DELETE CASCADE,
    user_id_ref VARCHAR(255) NOT NULL,
    user_name_snapshot VARCHAR(255), -- Denormalized from Auth Service
    total_items INTEGER DEFAULT 0,
    total_amount DECIMAL(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'INR',
    items JSONB DEFAULT '[]', -- Denormalized cart items with product info
    last_updated TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- Saved carts for later (abandoned cart recovery)
CREATE TABLE saved_carts (
    id SERIAL PRIMARY KEY,
    user_id_ref VARCHAR(255) NOT NULL,
    cart_data JSONB NOT NULL, -- Serialized cart state
    save_reason VARCHAR(100), -- 'abandoned', 'manual_save', 'session_timeout'
    expires_at TIMESTAMP
    WITH
        TIME ZONE,
        created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- Cross-service reference validation log
CREATE TABLE reference_validation_log (
    id SERIAL PRIMARY KEY,
    reference_type VARCHAR(50) NOT NULL, -- 'user', 'product'
    reference_id VARCHAR(255) NOT NULL,
    validation_status VARCHAR(50) NOT NULL, -- 'valid', 'invalid', 'not_found'
    validation_response JSONB,
    validated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        service_name VARCHAR(100) NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_carts_user_id_ref ON carts (user_id_ref);

CREATE INDEX idx_carts_session_id ON carts (session_id);

CREATE INDEX idx_carts_status ON carts (status);

CREATE INDEX idx_carts_expires_at ON carts (expires_at);

CREATE INDEX idx_cart_items_cart_id ON cart_items (cart_id);

CREATE INDEX idx_cart_items_product_id_ref ON cart_items (product_id_ref);

CREATE INDEX idx_cart_items_validation_status ON cart_items (validation_status);

CREATE INDEX idx_wishlists_user_id_ref ON wishlists (user_id_ref);

CREATE INDEX idx_wishlist_items_wishlist_id ON wishlist_items (wishlist_id);

CREATE INDEX idx_wishlist_items_product_id_ref ON wishlist_items (product_id_ref);

CREATE INDEX idx_cart_view_user_id_ref ON cart_view (user_id_ref);

CREATE INDEX idx_saved_carts_user_id_ref ON saved_carts (user_id_ref);

CREATE INDEX idx_saved_carts_expires_at ON saved_carts (expires_at);

CREATE INDEX idx_reference_validation_log_type_id ON reference_validation_log (reference_type, reference_id);

CREATE INDEX idx_reference_validation_log_validated_at ON reference_validation_log (validated_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_carts_updated_at BEFORE UPDATE ON carts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cart_items_updated_at BEFORE UPDATE ON cart_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wishlists_updated_at BEFORE UPDATE ON wishlists
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wishlist_items_updated_at BEFORE UPDATE ON wishlist_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update cart totals when items change
CREATE OR REPLACE FUNCTION update_cart_totals()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE carts 
    SET total_items = (
        SELECT COALESCE(SUM(quantity), 0) 
        FROM cart_items 
        WHERE cart_id = COALESCE(NEW.cart_id, OLD.cart_id)
    ),
    total_amount = (
        SELECT COALESCE(SUM(total_price), 0) 
        FROM cart_items 
        WHERE cart_id = COALESCE(NEW.cart_id, OLD.cart_id)
    ),
    updated_at = NOW()
    WHERE id = COALESCE(NEW.cart_id, OLD.cart_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Triggers to automatically update cart totals
CREATE TRIGGER update_cart_totals_on_insert AFTER INSERT ON cart_items
    FOR EACH ROW EXECUTE FUNCTION update_cart_totals();

CREATE TRIGGER update_cart_totals_on_update AFTER UPDATE ON cart_items
    FOR EACH ROW EXECUTE FUNCTION update_cart_totals();

CREATE TRIGGER update_cart_totals_on_delete AFTER DELETE ON cart_items
    FOR EACH ROW EXECUTE FUNCTION update_cart_totals();

-- Function to update wishlist totals when items change
CREATE OR REPLACE FUNCTION update_wishlist_totals()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE wishlists 
    SET total_items = (
        SELECT COUNT(*) 
        FROM wishlist_items 
        WHERE wishlist_id = COALESCE(NEW.wishlist_id, OLD.wishlist_id)
    ),
    updated_at = NOW()
    WHERE id = COALESCE(NEW.wishlist_id, OLD.wishlist_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Triggers to automatically update wishlist totals
CREATE TRIGGER update_wishlist_totals_on_insert AFTER INSERT ON wishlist_items
    FOR EACH ROW EXECUTE FUNCTION update_wishlist_totals();

CREATE TRIGGER update_wishlist_totals_on_delete AFTER DELETE ON wishlist_items
    FOR EACH ROW EXECUTE FUNCTION update_wishlist_totals();