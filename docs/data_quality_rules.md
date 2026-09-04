# Data Quality Rules

All rules are metadata-driven and configured in `profiling/quality_rules.py`. No rule logic is hardcoded inside individual check functions.

## Severity Levels

| Level | Meaning |
|-------|---------|
| CRITICAL | Must be resolved before warehouse load; pipeline should stop |
| HIGH | Significant business impact; must be resolved in transformation |
| MEDIUM | Noticeable data quality issue; resolve before reporting |
| LOW | Minor cosmetic issue; resolve in transformation |
| INFO | Advisory; requires manual review, not automatic correction |

## Quality Score Weights

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Completeness | 25% | Non-null rate for required/PK columns |
| Uniqueness | 20% | Absence of duplicate rows and PKs |
| Validity | 25% | Type correctness, valid values, formats |
| Consistency | 15% | Business rules, date sequences, whitespace |
| Referential Integrity | 15% | FK relationships between tables |

## Primary Key Rules

| Rule | Table | Column | Severity |
|------|-------|--------|----------|
| PK must not be null | All tables | PK column | CRITICAL |
| PK must be unique | All tables | PK column | CRITICAL |
| PK must be positive integer | All tables | PK column | CRITICAL |

## Business Rules

| Rule ID | Table | Columns | Condition | Severity | Business Reason |
|---------|-------|---------|-----------|----------|-----------------|
| RULE001 | products | unit_price | unit_price > 0 | HIGH | Zero/negative price corrupts revenue reporting |
| RULE002 | products | cost_price, unit_price | cost_price ≤ unit_price | MEDIUM | Cost above price implies loss; skews margin analysis |
| RULE003 | inventory | stock_quantity | stock_quantity ≥ 0 | HIGH | Negative stock is physically impossible |
| RULE004 | orders | total_amount | total_amount ≥ 0 | HIGH | Negative totals understate revenue |
| RULE005 | order_items | quantity | quantity > 0 | HIGH | A line with no quantity should not exist |
| RULE006 | payments | amount_paid | amount_paid ≥ 0 | HIGH | Negative payments distort cash reconciliation |
| RULE007 | returns | refund_amount | refund_amount ≥ 0 | HIGH | Negative refunds invert returns reporting |
| RULE008 | customers | date_of_birth | date_of_birth ≤ today | MEDIUM | Future birth date makes age segmentation meaningless |
| RULE009 | employees | hire_date | hire_date ≤ today | MEDIUM | Future hire dates break tenure reporting |
| RULE010 | shipments | shipment_date, delivery_date | delivery_date ≥ shipment_date | HIGH | Delivery before dispatch is physically impossible |
| RULE011 | order_items | net_amount, tax_amount, line_total | line_total = net_amount + tax_amount (±0.01) | HIGH | Inconsistent totals mean revenue and tax cannot be trusted |
| RULE012 | shipments (cross-table) | shipment_date → orders.order_date | shipment_date ≥ order_date | HIGH | Dispatch before order creation indicates a fault |
| RULE013 | payments (cross-table) | payment_date → orders.order_date | payment_date ≥ order_date | MEDIUM | Payment before order creation breaks order-to-cash timeline |

## Numeric Column Rules

| Table | Column | Constraint | Severity |
|-------|--------|-----------|----------|
| products | unit_price | > 0 | HIGH |
| products | cost_price | > 0 | HIGH |
| employees | salary | > 0 | HIGH |
| inventory | stock_quantity | ≥ 0 | HIGH |
| orders | total_amount | ≥ 0 | HIGH |
| order_items | quantity | > 0 | HIGH |
| order_items | unit_price | > 0 | HIGH |
| order_items | discount_pct | 0–100 | MEDIUM |
| order_items | tax_pct | 0–100 | MEDIUM |
| order_items | net_amount | ≥ 0 | HIGH |
| order_items | tax_amount | ≥ 0 | HIGH |
| order_items | line_total | ≥ 0 | HIGH |
| payments | amount_paid | ≥ 0 | HIGH |
| returns | refund_amount | ≥ 0 | HIGH |

## Categorical Domain Rules

| Table | Column | Allowed Values | Severity |
|-------|--------|---------------|----------|
| customers | gender | Male, Female, Other | MEDIUM |
| customers | status | Active, Inactive, Blocked | MEDIUM |
| products | status | Active, Discontinued, Out of Stock | MEDIUM |
| orders | order_status | Pending, Processing, Shipped, Delivered, Cancelled, Returned | MEDIUM |
| payments | payment_method | Credit Card, Debit Card, UPI, Net Banking, Cash, Wallet | MEDIUM |
| payments | payment_status | Pending, Completed, Failed, Refunded | MEDIUM |
| shipments | shipment_status | Dispatched, In Transit, Out for Delivery, Delivered, Failed | MEDIUM |

## Date Rules

| Column | Rule | Severity |
|--------|------|----------|
| customers.date_of_birth | Must not be future; must be after 1920-01-01 | MEDIUM |
| customers.registration_date | Must not be future; must be after 1900-01-01 | MEDIUM |
| products.created_date | Must not be future | MEDIUM |
| stores.opened_date | Must not be future | MEDIUM |
| employees.hire_date | Must not be future | MEDIUM |
| orders.order_date | Must not be future | MEDIUM |
| payments.payment_date | Must not be future; must be ≥ order_date (RULE013) | MEDIUM |
| shipments.shipment_date | Must not be future; must be ≥ order_date (RULE012) | HIGH |
| shipments.delivery_date | Must be ≥ shipment_date (RULE010); nullable by design | HIGH |
| returns.return_date | Must not be future | MEDIUM |

## String Quality Rules (all LOW severity)

| Check | Description |
|-------|-------------|
| LEADING_OR_TRAILING_WHITESPACE | Values with leading or trailing spaces |
| MULTIPLE_SPACES | Values containing consecutive spaces |
| EMPTY_STRING | Empty or whitespace-only string values |
| EXCESSIVE_LENGTH | Values exceeding the configured maximum length (default 255) |

## Email and Phone Rules

| Check | Condition | Severity |
|-------|-----------|----------|
| INVALID_EMAIL | Must match pattern `user@domain.tld` | MEDIUM |
| INVALID_PHONE | Must contain 7–15 digits, no letters | MEDIUM |

## Outlier Detection

IQR method with multiplier 1.5. Applied to:

| Table | Columns |
|-------|---------|
| products | unit_price, cost_price |
| employees | salary |
| inventory | stock_quantity |
| orders | total_amount |
| order_items | quantity, unit_price, line_total |
| payments | amount_paid |
| returns | refund_amount |

Status: `POTENTIAL_OUTLIER` at severity INFO. Never automatically excluded or corrected.

## Nullable by Design

These columns are allowed to be null and are excluded from null checks:

| Table | Column | Reason |
|-------|--------|--------|
| categories | description | Optional free-text |
| shipments | delivery_date | Null until delivered |
