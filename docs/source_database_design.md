# Source OLTP Database Design

## Database: `retail_oltp`

## Requirements

- **MySQL 8.0.16+** (CHECK constraints are only enforced from this version; earlier versions parse but silently ignore them)

## Overview

This document describes the transactional (OLTP) database that serves as the **source system** for our Retail ETL Pipeline. The database is designed to simulate a real-world e-commerce/retail company similar to Amazon, Flipkart, or Reliance Digital.

---

## ER Diagram (Mermaid)

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    STORES ||--o{ ORDERS : receives
    EMPLOYEES ||--o{ ORDERS : processes
    STORES ||--o{ EMPLOYEES : employs
    CATEGORIES ||--o{ PRODUCTS : contains
    SUPPLIERS ||--o{ PRODUCTS : supplies
    PRODUCTS ||--o{ ORDER_ITEMS : "is ordered in"
    ORDERS ||--o{ ORDER_ITEMS : contains
    ORDERS ||--o| PAYMENTS : "paid via"
    ORDERS ||--o| SHIPMENTS : "shipped as"
    ORDER_ITEMS ||--o| RETURNS : "returned as"
    PRODUCTS ||--o{ INVENTORY : "stocked in"
    STORES ||--o{ INVENTORY : holds

    CUSTOMERS {
        int customer_id PK
        varchar first_name
        varchar last_name
        enum gender
        varchar email UK
        varchar phone
        date date_of_birth
        varchar city
        varchar state
        varchar country
        date registration_date
        enum status
    }

    CATEGORIES {
        int category_id PK
        varchar category_name
        varchar description
    }

    SUPPLIERS {
        int supplier_id PK
        varchar supplier_name
        varchar contact_person
        varchar email UK
        varchar phone
        varchar city
        varchar country
    }

    PRODUCTS {
        int product_id PK
        int category_id FK
        int supplier_id FK
        varchar product_name
        varchar brand
        decimal unit_price
        decimal cost_price
        date created_date
        enum status
    }

    STORES {
        int store_id PK
        varchar store_name
        varchar city
        varchar state
        varchar manager_name
        date opened_date
    }

    EMPLOYEES {
        int employee_id PK
        int store_id FK
        varchar first_name
        varchar last_name
        varchar designation
        decimal salary
        date hire_date
    }

    INVENTORY {
        int inventory_id PK
        int product_id FK
        int store_id FK
        int stock_quantity
        datetime last_updated
    }

    ORDERS {
        int order_id PK
        int customer_id FK
        int store_id FK
        int employee_id FK
        datetime order_date
        enum order_status
        decimal total_amount
    }

    ORDER_ITEMS {
        int order_item_id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
        decimal discount_pct
        decimal tax_pct
        decimal net_amount
        decimal tax_amount
        decimal line_total
    }

    PAYMENTS {
        int payment_id PK
        int order_id FK_UK
        enum payment_method
        enum payment_status
        datetime payment_date
        decimal amount_paid
    }

    SHIPMENTS {
        int shipment_id PK
        int order_id FK_UK
        varchar shipping_partner
        varchar tracking_number UK
        date shipment_date
        date delivery_date
        enum shipment_status
    }

    RETURNS {
        int return_id PK
        int order_item_id FK_UK
        varchar return_reason
        date return_date
        decimal refund_amount
    }
```

---

## Table Relationships

| Parent Table | Child Table | Relationship | FK Column | Enforced By |
|---|---|---|---|---|
| customers | orders | One-to-Many | customer_id | FK |
| stores | orders | One-to-Many | store_id | FK |
| employees | orders | One-to-Many | employee_id | FK |
| stores | employees | One-to-Many | store_id | FK |
| categories | products | One-to-Many | category_id | FK |
| suppliers | products | One-to-Many | supplier_id | FK |
| orders | order_items | One-to-Many | order_id | FK |
| products | order_items | One-to-Many | product_id | FK |
| orders | payments | **One-to-One** | order_id | FK + UNIQUE |
| orders | shipments | **One-to-One** | order_id | FK + UNIQUE |
| order_items | returns | **One-to-One** | order_item_id | FK + UNIQUE |
| products | inventory | One-to-Many (unique grain) | product_id | FK + UNIQUE(product_id, store_id) |
| stores | inventory | One-to-Many (unique grain) | store_id | FK + UNIQUE(product_id, store_id) |

---

## Why Each Table Exists

### 1. `customers`
Stores all registered customer profiles. Every order must be associated with a customer. Supports customer segmentation, geographic analysis, and lifecycle tracking.

### 2. `categories`
Classifies products into logical groups (Electronics, Clothing, etc.). Enables category-level reporting, filtering, and inventory management.

### 3. `suppliers`
Tracks vendors who provide products. Supports supplier performance analysis, procurement tracking, and cost management.

### 4. `products`
The product catalog with pricing information. Central to the business — connects categories, suppliers, inventory, and order items.

### 5. `stores`
Physical retail locations. Each order and employee belongs to a store. Supports store-level performance comparison.

### 6. `employees`
Store staff who process orders. Enables employee performance tracking, workload analysis, and payroll.

### 7. `inventory`
Stock levels per product per store. The `UNIQUE(product_id, store_id)` constraint enforces the grain — exactly one row per product per store.

### 8. `orders`
The core transaction table. Records every customer purchase with timestamp, status, and total amount. Note: `total_amount` is tax-inclusive (sum of `line_total` from order_items).

### 9. `order_items`
Line-level detail for each order. Key columns:
- `discount_pct`: percentage discount (0-100), named explicitly to avoid confusion with currency amounts
- `tax_pct`: tax percentage (e.g., 18 for GST), bounded 0-100
- `net_amount`: pre-tax amount = `quantity * unit_price * (1 - discount_pct/100)`
- `tax_amount`: tax in currency = `net_amount * tax_pct / 100`
- `line_total`: final amount = `net_amount + tax_amount`

This split enables the warehouse to report net revenue, tax liability, and gross revenue independently.

### 10. `payments`
One payment per order (enforced by UNIQUE on `order_id`). Tracks payment method, status, and amount. `amount_paid` equals `orders.total_amount` (tax-inclusive). Cancelled/Returned orders have status 'Refunded'.

### 11. `shipments`
One shipment per order (enforced by UNIQUE on `order_id`). Only exists for orders with status Shipped, Delivered, or Returned.

### 12. `returns`
One return per order item (enforced by UNIQUE on `order_item_id`). Only exists for items in orders with status 'Returned'. `refund_amount` equals the item's `line_total`.

---

## Normalization Explanation

This database is designed to **Third Normal Form (3NF)**:

### 1NF (First Normal Form)
- All columns contain atomic (single) values
- Each row is uniquely identified by a primary key
- No repeating groups or arrays

### 2NF (Second Normal Form)
- Satisfies 1NF
- All non-key columns are fully dependent on the entire primary key
- Example: `order_items` separates line-level data from order-level data

### 3NF (Third Normal Form)
- Satisfies 2NF
- No transitive dependencies — non-key columns depend only on the primary key
- Example: `supplier_name` is in `suppliers` table, not in `products` table
- Example: `category_name` is in `categories` table, not in `products` table

### Why 3NF for OLTP?
- **Minimizes data redundancy** — each fact is stored once
- **Prevents update anomalies** — changes only need one update
- **Ensures data integrity** — foreign keys enforce relationships
- **Optimized for writes** — INSERT/UPDATE operations are fast

---

## How This Database Supports ETL

### Extract Phase
- Clean, well-structured tables make extraction straightforward
- Primary keys provide reliable row identification
- `order_date`, `registration_date`, and `last_updated` columns enable **incremental extraction**
- Status columns (`order_status`, `payment_status`) support **CDC (Change Data Capture)**

### Transform Phase
- Normalized structure requires JOINs, which the Transform layer will denormalize
- `net_amount` / `tax_amount` / `line_total` split enables clean revenue calculations
- `discount_pct` / `tax_pct` naming prevents percent-vs-amount confusion
- Geographic data (city, state) supports regional aggregation
- Date columns support time-based dimension building
- **Note:** Cancelled/Returned orders retain their `total_amount`; the transform layer must filter by `order_status` to exclude them from revenue calculations

### Load Phase (Target: Data Warehouse)
- Customer data → `dim_customer` (SCD Type 2)
- Product + Category + Supplier → `dim_product`
- Store data → `dim_store`
- Date columns → `dim_date`
- Orders + Items + Payments → `fact_sales` (using `net_amount` for revenue, `tax_amount` for tax)
- Returns → `fact_returns`
- Inventory → `fact_inventory_snapshot`

### ETL-Friendly Design Decisions
1. **AUTO_INCREMENT PKs** — Simple surrogate keys for extraction
2. **NOT NULL constraints** — Reduces null handling in transforms
3. **ENUM types** — Consistent status values, easy to map
4. **Datetime columns** — Enable incremental/delta loads
5. **Decimal precision** — Financial accuracy preserved through pipeline
6. **InnoDB engine** — Consistent reads during extraction (MVCC)
7. **Separate net/tax/total** — Warehouse can report any revenue slice directly

---

## Sample Data Summary

| Table | Expected Count | Notes |
|---|---|---|
| customers | 100 | Realistic Indian names, multiple cities |
| categories | 10 | Standard retail categories |
| suppliers | 10 | One per category |
| products | 50 | 5 per category with real brands |
| stores | 5 | Major Indian cities |
| employees | 20 | 4 per store |
| inventory | 60 | Products 1-10 get 2 stores, 11-50 get 1 store |
| orders | 500 | Distributed across 2024 |
| order_items | ~1000 | 1-3 items per order (avg 2.0) |
| payments | ~500 | One per order (skips any with zero total) |
| shipments | ~340 | For Shipped, Delivered, and Returned orders |
| returns | ~80-120 | One per item in Returned orders |

---

## SQL Files

| File | Purpose |
|---|---|
| `create_database.sql` | Drops (if exists) and creates `retail_oltp` — the only reset path |
| `create_tables.sql` | Creates all 12 tables with proper data types |
| `constraints.sql` | Adds FK, UNIQUE, and CHECK constraints |
| `indexes.sql` | Creates non-redundant performance indexes (FK indexes excluded) |
| `sample_data.sql` | Inserts realistic sample data via stored procedures |

### Execution Order

Run in MySQL Workbench or mysql CLI (in order):

```sql
-- 1. Create database (drops existing!)
source sql/source/create_database.sql

-- 2. Create tables
source sql/source/create_tables.sql

-- 3. Add constraints
source sql/source/constraints.sql

-- 4. Add indexes
source sql/source/indexes.sql

-- 5. Insert sample data
source sql/source/sample_data.sql
```

> **Important:** `sample_data.sql` uses `DELIMITER` blocks for stored procedures.
> It can only be executed via MySQL Workbench or the `mysql` command-line client.
> It **cannot** be executed through SQLAlchemy or mysql-connector-python.

> **Re-runnable:** Only `create_database.sql` is re-runnable (it drops everything).
> All other scripts fail on a second run due to duplicate objects.

---

## Design Principles Applied

1. **Referential Integrity** — All FKs enforced with appropriate ON UPDATE/DELETE actions
2. **One-to-One enforcement** — UNIQUE constraints on payments.order_id, shipments.order_id, returns.order_item_id
3. **Grain enforcement** — UNIQUE(product_id, store_id) on inventory prevents duplicate stock rows
4. **Data Validation** — CHECK constraints prevent invalid data (MySQL 8.0.16+ required)
5. **Clear naming** — `discount_pct`/`tax_pct` for percentages, `net_amount`/`tax_amount`/`line_total` for currency
6. **No redundant indexes** — FK-backed indexes are not duplicated in indexes.sql
7. **Performance** — Indexes on commonly queried non-FK columns (dates, status, names)
8. **Scalability** — AUTO_INCREMENT, InnoDB engine, proper indexing
9. **ETL-Ready** — Timestamps, status fields, net/tax split for clean warehouse loading
