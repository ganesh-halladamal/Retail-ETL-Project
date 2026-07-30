-- ===========================================
-- Retail ETL Project - Source OLTP Database
-- File: constraints.sql
-- Purpose: Add FK, UNIQUE, and CHECK constraints
-- ===========================================

USE retail_oltp;

-- ===========================================
-- UNIQUE CONSTRAINTS
-- ===========================================

-- Customer email must be unique
ALTER TABLE customers
    ADD CONSTRAINT uq_customers_email UNIQUE (email);

-- Supplier email must be unique
ALTER TABLE suppliers
    ADD CONSTRAINT uq_suppliers_email UNIQUE (email);

-- Shipment tracking number must be unique
ALTER TABLE shipments
    ADD CONSTRAINT uq_shipments_tracking UNIQUE (tracking_number);

-- ===========================================
-- FOREIGN KEY CONSTRAINTS
-- ===========================================

-- Products → Categories
ALTER TABLE products
    ADD CONSTRAINT fk_products_category
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

-- Products → Suppliers
ALTER TABLE products
    ADD CONSTRAINT fk_products_supplier
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

-- Employees → Stores
ALTER TABLE employees
    ADD CONSTRAINT fk_employees_store
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

-- Inventory → Products
ALTER TABLE inventory
    ADD CONSTRAINT fk_inventory_product
    FOREIGN KEY (product_id) REFERENCES products(product_id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

-- Inventory → Stores
ALTER TABLE inventory
    ADD CONSTRAINT fk_inventory_store
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

-- Orders → Customers
ALTER TABLE orders
    ADD CONSTRAINT fk_orders_customer
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

-- Orders → Stores
ALTER TABLE orders
    ADD CONSTRAINT fk_orders_store
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

-- Orders → Employees
ALTER TABLE orders
    ADD CONSTRAINT fk_orders_employee
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

-- Order Items → Orders
ALTER TABLE order_items
    ADD CONSTRAINT fk_order_items_order
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
    ON UPDATE CASCADE ON DELETE CASCADE;

-- Order Items → Products
ALTER TABLE order_items
    ADD CONSTRAINT fk_order_items_product
    FOREIGN KEY (product_id) REFERENCES products(product_id)
    ON UPDATE CASCADE ON DELETE RESTRICT;

-- Payments → Orders
ALTER TABLE payments
    ADD CONSTRAINT fk_payments_order
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
    ON UPDATE CASCADE ON DELETE CASCADE;

-- Shipments → Orders
ALTER TABLE shipments
    ADD CONSTRAINT fk_shipments_order
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
    ON UPDATE CASCADE ON DELETE CASCADE;

-- Returns → Order Items
ALTER TABLE returns
    ADD CONSTRAINT fk_returns_order_item
    FOREIGN KEY (order_item_id) REFERENCES order_items(order_item_id)
    ON UPDATE CASCADE ON DELETE CASCADE;

-- ===========================================
-- CHECK CONSTRAINTS
-- ===========================================

-- Products: unit_price must be positive
ALTER TABLE products
    ADD CONSTRAINT chk_products_unit_price
    CHECK (unit_price > 0);

-- Products: cost_price must be positive
ALTER TABLE products
    ADD CONSTRAINT chk_products_cost_price
    CHECK (cost_price > 0);

-- Employees: salary must be positive
ALTER TABLE employees
    ADD CONSTRAINT chk_employees_salary
    CHECK (salary > 0);

-- Inventory: stock cannot be negative
ALTER TABLE inventory
    ADD CONSTRAINT chk_inventory_stock
    CHECK (stock_quantity >= 0);

-- Order Items: quantity must be at least 1
ALTER TABLE order_items
    ADD CONSTRAINT chk_order_items_quantity
    CHECK (quantity >= 1);

-- Order Items: discount between 0 and 100
ALTER TABLE order_items
    ADD CONSTRAINT chk_order_items_discount
    CHECK (discount >= 0 AND discount <= 100);

-- Order Items: tax must be non-negative
ALTER TABLE order_items
    ADD CONSTRAINT chk_order_items_tax
    CHECK (tax >= 0);

-- Payments: amount must be positive
ALTER TABLE payments
    ADD CONSTRAINT chk_payments_amount
    CHECK (amount_paid > 0);

-- Returns: refund must be positive
ALTER TABLE returns
    ADD CONSTRAINT chk_returns_refund
    CHECK (refund_amount > 0);

-- Orders: total_amount must be non-negative
ALTER TABLE orders
    ADD CONSTRAINT chk_orders_total
    CHECK (total_amount >= 0);

SELECT 'All constraints applied successfully.' AS status;
