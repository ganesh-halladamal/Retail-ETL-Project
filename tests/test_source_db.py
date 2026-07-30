"""
===========================================
Tests - Source Database Integrity
===========================================
Validates that the retail_oltp database is loaded
correctly with expected counts and no orphan rows.

Run: pytest tests/test_source_db.py -v
Requires: retail_oltp database populated with sample data.
"""

import pytest
from sqlalchemy import create_engine, text
from config import get_connection_string


@pytest.fixture(scope="module")
def engine():
    """Create SQLAlchemy engine for retail_oltp."""
    url = get_connection_string("retail_oltp")
    eng = create_engine(url)
    yield eng
    eng.dispose()


@pytest.fixture(scope="module")
def connection(engine):
    """Provide a database connection."""
    with engine.connect() as conn:
        yield conn


class TestTablesExist:
    """Verify all 12 tables are present."""

    EXPECTED_TABLES = [
        "customers", "categories", "products", "suppliers",
        "stores", "employees", "inventory", "orders",
        "order_items", "payments", "shipments", "returns",
    ]

    def test_all_tables_exist(self, connection) -> None:
        result = connection.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        for table in self.EXPECTED_TABLES:
            assert table in tables, f"Table '{table}' not found in database"


class TestRowCounts:
    """Verify row counts are within expected ranges."""

    def test_customers_count(self, connection) -> None:
        count = connection.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        assert count == 100

    def test_products_count(self, connection) -> None:
        count = connection.execute(text("SELECT COUNT(*) FROM products")).scalar()
        assert count == 50

    def test_categories_count(self, connection) -> None:
        count = connection.execute(text("SELECT COUNT(*) FROM categories")).scalar()
        assert count == 10

    def test_suppliers_count(self, connection) -> None:
        count = connection.execute(text("SELECT COUNT(*) FROM suppliers")).scalar()
        assert count == 10

    def test_stores_count(self, connection) -> None:
        count = connection.execute(text("SELECT COUNT(*) FROM stores")).scalar()
        assert count == 5

    def test_employees_count(self, connection) -> None:
        count = connection.execute(text("SELECT COUNT(*) FROM employees")).scalar()
        assert count == 20

    def test_orders_count(self, connection) -> None:
        count = connection.execute(text("SELECT COUNT(*) FROM orders")).scalar()
        assert count == 500

    def test_inventory_count(self, connection) -> None:
        count = connection.execute(text("SELECT COUNT(*) FROM inventory")).scalar()
        assert count == 60

    def test_order_items_count(self, connection) -> None:
        """Order items should be approximately 1000 (500 orders * avg 2 items)."""
        count = connection.execute(text("SELECT COUNT(*) FROM order_items")).scalar()
        assert 800 <= count <= 1200, f"Expected ~1000 order items, got {count}"

    def test_payments_count(self, connection) -> None:
        """Each order with items should have exactly one payment."""
        count = connection.execute(text("SELECT COUNT(*) FROM payments")).scalar()
        assert 450 <= count <= 500, f"Expected ~500 payments, got {count}"

    def test_shipments_count(self, connection) -> None:
        """Shipments for Shipped + Delivered + Returned orders (~60% of 500)."""
        count = connection.execute(text("SELECT COUNT(*) FROM shipments")).scalar()
        assert 250 <= count <= 400, f"Expected ~340 shipments, got {count}"

    def test_returns_count(self, connection) -> None:
        """Returns for items in Returned orders (~8% of orders * avg 2 items)."""
        count = connection.execute(text("SELECT COUNT(*) FROM returns")).scalar()
        assert 30 <= count <= 200, f"Expected ~80-120 returns, got {count}"


class TestReferentialIntegrity:
    """Verify no orphan rows exist across FK relationships."""

    def test_no_orders_without_items(self, connection) -> None:
        """Every order should have at least one order item."""
        result = connection.execute(text("""
            SELECT COUNT(*) FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE oi.order_item_id IS NULL
        """))
        assert result.scalar() == 0, "Found orders without any order items"

    def test_no_orders_without_payments(self, connection) -> None:
        """Every order with total > 0 should have a payment."""
        result = connection.execute(text("""
            SELECT COUNT(*) FROM orders o
            LEFT JOIN payments p ON o.order_id = p.order_id
            WHERE p.payment_id IS NULL AND o.total_amount > 0
        """))
        assert result.scalar() == 0, "Found orders with amount but no payment"

    def test_no_orphan_order_items(self, connection) -> None:
        """Every order_item should reference a valid order."""
        result = connection.execute(text("""
            SELECT COUNT(*) FROM order_items oi
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL
        """))
        assert result.scalar() == 0, "Found order items pointing to non-existent orders"

    def test_no_orphan_payments(self, connection) -> None:
        """Every payment should reference a valid order."""
        result = connection.execute(text("""
            SELECT COUNT(*) FROM payments p
            LEFT JOIN orders o ON p.order_id = o.order_id
            WHERE o.order_id IS NULL
        """))
        assert result.scalar() == 0, "Found payments pointing to non-existent orders"

    def test_shipped_orders_have_shipments(self, connection) -> None:
        """Orders with Shipped/Delivered/Returned status should have shipments."""
        result = connection.execute(text("""
            SELECT COUNT(*) FROM orders o
            LEFT JOIN shipments s ON o.order_id = s.order_id
            WHERE o.order_status IN ('Shipped', 'Delivered', 'Returned')
              AND s.shipment_id IS NULL
        """))
        assert result.scalar() == 0, "Found shipped/delivered orders without shipments"

    def test_returned_items_have_returns(self, connection) -> None:
        """Order items in Returned orders should have return records."""
        result = connection.execute(text("""
            SELECT COUNT(*) FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            LEFT JOIN returns r ON oi.order_item_id = r.order_item_id
            WHERE o.order_status = 'Returned' AND r.return_id IS NULL
        """))
        assert result.scalar() == 0, "Found returned order items without return records"

    def test_products_have_valid_categories(self, connection) -> None:
        """Every product should reference a valid category."""
        result = connection.execute(text("""
            SELECT COUNT(*) FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            WHERE c.category_id IS NULL
        """))
        assert result.scalar() == 0, "Found products with invalid category_id"

    def test_employees_belong_to_valid_stores(self, connection) -> None:
        """Every employee should reference a valid store."""
        result = connection.execute(text("""
            SELECT COUNT(*) FROM employees e
            LEFT JOIN stores s ON e.store_id = s.store_id
            WHERE s.store_id IS NULL
        """))
        assert result.scalar() == 0, "Found employees with invalid store_id"
