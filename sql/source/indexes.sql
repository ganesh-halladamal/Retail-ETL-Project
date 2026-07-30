-- ===========================================
-- Retail ETL Project - Source OLTP Database
-- File: indexes.sql
-- Purpose: Create indexes for query performance
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
-- ===========================================
-- Search by product name
CREATE INDEX idx_products_name
    ON products(product_name);

-- Filter by brand
CREATE INDEX idx_products_brand
    ON products(brand);

-- Filter by category (joins with categories)
CREATE INDEX idx_products_category
    ON products(category_id);

-- Filter by supplier
CREATE INDEX idx_products_supplier
    ON products(supplier_id);

-- Filter by status
CREATE INDEX idx_products_status
    ON products(status);

-- ===========================================
-- ORDERS INDEXES
-- ===========================================
-- Filter by customer (customer order history)
CREATE INDEX idx_orders_customer
    ON orders(customer_id);

-- Filter by store
CREATE INDEX idx_orders_store
    ON orders(store_id);

-- Filter by employee
CREATE INDEX idx_orders_employee
    ON orders(employee_id);

-- Filter by order date (date range reports)
CREATE INDEX idx_orders_date
    ON orders(order_date);

-- Filter by status
CREATE INDEX idx_orders_status
    ON orders(order_status);

-- Composite: date + status (common report query)
CREATE INDEX idx_orders_date_status
    ON orders(order_date, order_status);

-- ===========================================
-- ORDER_ITEMS INDEXES
-- ===========================================
-- Filter by order (order details lookup)
CREATE INDEX idx_order_items_order
    ON order_items(order_id);

-- Filter by product (product sales analysis)
CREATE INDEX idx_order_items_product
    ON order_items(product_id);

-- ===========================================
-- PAYMENTS INDEXES
-- ===========================================
-- Filter by order
CREATE INDEX idx_payments_order
    ON payments(order_id);

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
-- INVENTORY INDEXES
-- ===========================================
-- Filter by product
CREATE INDEX idx_inventory_product
    ON inventory(product_id);

-- Filter by store
CREATE INDEX idx_inventory_store
    ON inventory(store_id);

-- Composite: product + store (stock lookup)
CREATE INDEX idx_inventory_product_store
    ON inventory(product_id, store_id);

-- ===========================================
-- SHIPMENTS INDEXES
-- ===========================================
-- Filter by order
CREATE INDEX idx_shipments_order
    ON shipments(order_id);

-- Filter by status
CREATE INDEX idx_shipments_status
    ON shipments(shipment_status);

-- Filter by shipment date
CREATE INDEX idx_shipments_date
    ON shipments(shipment_date);

-- ===========================================
-- RETURNS INDEXES
-- ===========================================
-- Filter by order item
CREATE INDEX idx_returns_order_item
    ON returns(order_item_id);

-- Filter by return date
CREATE INDEX idx_returns_date
    ON returns(return_date);

-- ===========================================
-- EMPLOYEES INDEXES
-- ===========================================
-- Filter by store
CREATE INDEX idx_employees_store
    ON employees(store_id);

-- Filter by designation
CREATE INDEX idx_employees_designation
    ON employees(designation);

SELECT 'All indexes created successfully.' AS status;
