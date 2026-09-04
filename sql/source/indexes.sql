-- ===========================================
-- Retail ETL Project - Source OLTP Database
-- File: indexes.sql
-- Purpose: Create indexes for query performance
-- Note: Run AFTER constraints.sql. Only indexes
--       NOT already created by FK constraints
--       are included here to avoid redundancy.
-- Note: MySQL auto-creates indexes for FK columns,
--       so this file only adds non-FK indexes.
-- Requires: MySQL 8.0.16+ (for CHECK constraint enforcement)
-- Reset: Run create_database.sql to drop & recreate
-- ===========================================

USE retail_oltp;

-- ===========================================
-- CUSTOMERS INDEXES
-- ===========================================
-- Search by name (partial match lookups)
CREATE INDEX idx_customers_name
    ON customers(last_name, first_name);

-- Filter by city/state (geographic reports)
CREATE INDEX idx_customers_location
    ON customers(city, state);

-- Filter by status
CREATE INDEX idx_customers_status
    ON customers(status);

-- Filter by registration date (date range queries)
CREATE INDEX idx_customers_reg_date
    ON customers(registration_date);

-- ===========================================
-- PRODUCTS INDEXES
-- (category_id and supplier_id already indexed by FK)
-- ===========================================
-- Search by product name
CREATE INDEX idx_products_name
    ON products(product_name);

-- Filter by brand
CREATE INDEX idx_products_brand
    ON products(brand);

-- Filter by status
CREATE INDEX idx_products_status
    ON products(status);

-- ===========================================
-- ORDERS INDEXES
-- (customer_id, store_id, employee_id already indexed by FK)
-- ===========================================
-- Composite: date + status (covers date-only and date+status queries)
CREATE INDEX idx_orders_date_status
    ON orders(order_date, order_status);

-- Filter by status alone
CREATE INDEX idx_orders_status
    ON orders(order_status);

-- ===========================================
-- ORDER_ITEMS INDEXES
-- (order_id and product_id already indexed by FK)
-- ===========================================
-- No additional indexes needed; FK indexes cover lookups

-- ===========================================
-- PAYMENTS INDEXES
-- (order_id already indexed by FK)
-- ===========================================
-- Filter by payment date
CREATE INDEX idx_payments_date
    ON payments(payment_date);

-- Filter by method (payment method analysis)
CREATE INDEX idx_payments_method
    ON payments(payment_method);

-- Filter by status
CREATE INDEX idx_payments_status
    ON payments(payment_status);

-- ===========================================
-- SHIPMENTS INDEXES
-- (order_id already indexed by FK)
-- ===========================================
-- Filter by status
CREATE INDEX idx_shipments_status
    ON shipments(shipment_status);

-- Filter by shipment date
CREATE INDEX idx_shipments_date
    ON shipments(shipment_date);

-- ===========================================
-- RETURNS INDEXES
-- (order_item_id already indexed by FK)
-- ===========================================
-- Filter by return date
CREATE INDEX idx_returns_date
    ON returns(return_date);

-- ===========================================
-- EMPLOYEES INDEXES
-- (store_id already indexed by FK)
-- ===========================================
-- Filter by designation
CREATE INDEX idx_employees_designation
    ON employees(designation);

SELECT 'All indexes created successfully.' AS status;
