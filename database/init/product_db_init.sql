-- Product Service Database Initialization Script
-- This script creates the necessary tables for the Product Service

-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    image_url TEXT,
    parent_category_id INTEGER REFERENCES categories (id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    mrp DECIMAL(10,2) NOT NULL CHECK (mrp >= 0),
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    image_url TEXT,
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    unit VARCHAR(50) DEFAULT 'piece',
    sku VARCHAR(100) UNIQUE,
    weight DECIMAL(8,3),
    dimensions JSONB, -- {length, width, height}
    tags TEXT[],
    is_active BOOLEAN DEFAULT true,
    is_featured BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Product inventory tracking table
CREATE TABLE product_inventory (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    quantity_change INTEGER NOT NULL,
    new_quantity INTEGER NOT NULL CHECK (new_quantity >= 0),
    change_type VARCHAR(50) NOT NULL CHECK (
        change_type IN (
            'restock',
            'sale',
            'adjustment',
            'return',
            'damage'
        )
    ),
    reference_id VARCHAR(255), -- Order ID, adjustment ID, etc.
    notes TEXT,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        created_by VARCHAR(255) -- User ID who made the change
);

-- Product images table for multiple images per product
CREATE TABLE product_images (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    alt_text VARCHAR(255),
    is_primary BOOLEAN DEFAULT false,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW()
);

-- Product variants table (for size, color, etc.)
CREATE TABLE product_variants (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    variant_name VARCHAR(100) NOT NULL, -- e.g., "Size", "Color"
    variant_value VARCHAR(100) NOT NULL, -- e.g., "Large", "Red"
    price_adjustment DECIMAL(10, 2) DEFAULT 0,
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    sku VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW(),
        UNIQUE (
            product_id,
            variant_name,
            variant_value
        )
);

-- Indexes for performance
CREATE INDEX idx_products_category_id ON products (category_id);

CREATE INDEX idx_products_active ON products (is_active);

CREATE INDEX idx_products_featured ON products (is_featured);

CREATE INDEX idx_products_price ON products (price);

CREATE INDEX idx_products_stock ON products (stock_quantity);

CREATE INDEX idx_products_sku ON products (sku);

CREATE INDEX idx_categories_active ON categories (is_active);

CREATE INDEX idx_categories_parent ON categories (parent_category_id);

CREATE INDEX idx_product_inventory_product_id ON product_inventory (product_id);

CREATE INDEX idx_product_inventory_created_at ON product_inventory (created_at);

CREATE INDEX idx_product_images_product_id ON product_images (product_id);

CREATE INDEX idx_product_variants_product_id ON product_variants (product_id);

-- Full-text search index for products
CREATE INDEX idx_products_search ON products USING gin (
    to_tsvector (
        'english',
        name || ' ' || COALESCE(description, '')
    )
);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_variants_updated_at BEFORE UPDATE ON product_variants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update product stock quantity when inventory changes
CREATE OR REPLACE FUNCTION update_product_stock()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE products 
    SET stock_quantity = NEW.new_quantity,
        updated_at = NOW()
    WHERE id = NEW.product_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update product stock
CREATE TRIGGER update_product_stock_trigger AFTER INSERT ON product_inventory
    FOR EACH ROW EXECUTE FUNCTION update_product_stock();

-- Insert sample categories
INSERT INTO
    categories (name, description, is_active)
VALUES (
        'Electronics',
        'Electronic devices and accessories',
        true
    ),
    (
        'Clothing',
        'Apparel and fashion items',
        true
    ),
    (
        'Home & Garden',
        'Home improvement and gardening supplies',
        true
    ),
    (
        'Books',
        'Books and educational materials',
        true
    ),
    (
        'Sports',
        'Sports equipment and accessories',
        true
    ) ON CONFLICT (name) DO NOTHING;