-- ===========================================
-- Retail ETL Project - Source OLTP Database
-- File: create_tables.sql
-- Purpose: Create all transactional tables
-- Engine: InnoDB (supports transactions & FK)
-- ===========================================

USE retail_oltp;

-- ===========================================
-- 1. CUSTOMERS TABLE
-- Stores customer registration and profile data
-- ===========================================
CREATE TABLE customers (
    customer_id     INT             AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    gender          ENUM('Male', 'Female', 'Other') NOT NULL,
    email           VARCHAR(100)    NOT NULL,
    phone           VARCHAR(20)     NOT NULL,
    date_of_birth   DATE            NOT NULL,
    city            VARCHAR(50)     NOT NULL,
    state           VARCHAR(50)     NOT NULL,
    country         VARCHAR(50)     NOT NULL DEFAULT 'India',
    registration_date DATE          NOT NULL,
    status          ENUM('Active', 'Inactive', 'Blocked') NOT NULL DEFAULT 'Active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 2. CATEGORIES TABLE
-- Product categories for classification
-- ===========================================
CREATE TABLE categories (
    category_id     INT             AUTO_INCREMENT PRIMARY KEY,
    category_name   VARCHAR(100)    NOT NULL,
    description     VARCHAR(255)    NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 3. SUPPLIERS TABLE
-- Vendors who supply products
-- ===========================================
CREATE TABLE suppliers (
    supplier_id     INT             AUTO_INCREMENT PRIMARY KEY,
    supplier_name   VARCHAR(100)    NOT NULL,
    contact_person  VARCHAR(100)    NOT NULL,
    email           VARCHAR(100)    NOT NULL,
    phone           VARCHAR(20)     NOT NULL,
    city            VARCHAR(50)     NOT NULL,
    country         VARCHAR(50)     NOT NULL DEFAULT 'India'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 4. PRODUCTS TABLE
-- Product catalog with pricing
-- ===========================================
CREATE TABLE products (
    product_id      INT             AUTO_INCREMENT PRIMARY KEY,
    category_id     INT             NOT NULL,
    supplier_id     INT             NOT NULL,
    product_name    VARCHAR(150)    NOT NULL,
    brand           VARCHAR(100)    NOT NULL,
    unit_price      DECIMAL(10, 2)  NOT NULL,
    cost_price      DECIMAL(10, 2)  NOT NULL,
    created_date    DATE            NOT NULL,
    status          ENUM('Active', 'Discontinued', 'Out of Stock') NOT NULL DEFAULT 'Active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 5. STORES TABLE
-- Physical retail store locations
-- ===========================================
CREATE TABLE stores (
    store_id        INT             AUTO_INCREMENT PRIMARY KEY,
    store_name      VARCHAR(100)    NOT NULL,
    city            VARCHAR(50)     NOT NULL,
    state           VARCHAR(50)     NOT NULL,
    manager_name    VARCHAR(100)    NOT NULL,
    opened_date     DATE            NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 6. EMPLOYEES TABLE
-- Store employees and their details
-- ===========================================
CREATE TABLE employees (
    employee_id     INT             AUTO_INCREMENT PRIMARY KEY,
    store_id        INT             NOT NULL,
    first_name      VARCHAR(50)     NOT NULL,
    last_name       VARCHAR(50)     NOT NULL,
    designation     VARCHAR(50)     NOT NULL,
    salary          DECIMAL(10, 2)  NOT NULL,
    hire_date       DATE            NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 7. INVENTORY TABLE
-- Stock levels per product per store
-- ===========================================
CREATE TABLE inventory (
    inventory_id    INT             AUTO_INCREMENT PRIMARY KEY,
    product_id      INT             NOT NULL,
    store_id        INT             NOT NULL,
    stock_quantity  INT             NOT NULL DEFAULT 0,
    last_updated    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 8. ORDERS TABLE
-- Customer purchase orders
-- ===========================================
CREATE TABLE orders (
    order_id        INT             AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT             NOT NULL,
    store_id        INT             NOT NULL,
    employee_id     INT             NOT NULL,
    order_date      DATETIME        NOT NULL,
    order_status    ENUM('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled', 'Returned') NOT NULL DEFAULT 'Pending',
    total_amount    DECIMAL(12, 2)  NOT NULL DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 9. ORDER_ITEMS TABLE
-- Individual line items within an order
-- ===========================================
CREATE TABLE order_items (
    order_item_id   INT             AUTO_INCREMENT PRIMARY KEY,
    order_id        INT             NOT NULL,
    product_id      INT             NOT NULL,
    quantity        INT             NOT NULL DEFAULT 1,
    unit_price      DECIMAL(10, 2)  NOT NULL,
    discount        DECIMAL(5, 2)   NOT NULL DEFAULT 0.00,
    tax             DECIMAL(5, 2)   NOT NULL DEFAULT 0.00,
    line_total      DECIMAL(10, 2)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 10. PAYMENTS TABLE
-- Payment records for orders
-- ===========================================
CREATE TABLE payments (
    payment_id      INT             AUTO_INCREMENT PRIMARY KEY,
    order_id        INT             NOT NULL,
    payment_method  ENUM('Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash', 'Wallet') NOT NULL,
    payment_status  ENUM('Pending', 'Completed', 'Failed', 'Refunded') NOT NULL DEFAULT 'Pending',
    payment_date    DATETIME        NOT NULL,
    amount_paid     DECIMAL(12, 2)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 11. SHIPMENTS TABLE
-- Delivery tracking for orders
-- ===========================================
CREATE TABLE shipments (
    shipment_id     INT             AUTO_INCREMENT PRIMARY KEY,
    order_id        INT             NOT NULL,
    shipping_partner VARCHAR(100)   NOT NULL,
    tracking_number VARCHAR(50)     NOT NULL,
    shipment_date   DATE            NOT NULL,
    delivery_date   DATE            NULL,
    shipment_status ENUM('Dispatched', 'In Transit', 'Out for Delivery', 'Delivered', 'Failed') NOT NULL DEFAULT 'Dispatched'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ===========================================
-- 12. RETURNS TABLE
-- Product return records
-- ===========================================
CREATE TABLE returns (
    return_id       INT             AUTO_INCREMENT PRIMARY KEY,
    order_item_id   INT             NOT NULL,
    return_reason   VARCHAR(255)    NOT NULL,
    return_date     DATE            NOT NULL,
    refund_amount   DECIMAL(10, 2)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'All 12 tables created successfully.' AS status;
