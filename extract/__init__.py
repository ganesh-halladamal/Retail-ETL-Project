"""
===========================================
Extract Module
===========================================
This module handles data extraction from
various source systems (databases, files, APIs).

Layout:
    db_connection.py    Pooled SQLAlchemy engine for retail_oltp
    base_extractor.py   Shared extract + validate helpers
    extract_<table>.py  One thin module per source table
    extractor.py        Master orchestrator (extract_all)

Usage:
    from extract.extractor import extract_all, close

    data = extract_all()
    close()
"""

from extract import (
    base_extractor,
    db_connection,
    extract_categories,
    extract_customers,
    extract_employees,
    extract_inventory,
    extract_order_items,
    extract_orders,
    extract_payments,
    extract_products,
    extract_returns,
    extract_shipments,
    extract_stores,
    extract_suppliers,
)

__all__ = [
    "base_extractor",
    "db_connection",
    "extract_categories",
    "extract_customers",
    "extract_employees",
    "extract_inventory",
    "extract_order_items",
    "extract_orders",
    "extract_payments",
    "extract_products",
    "extract_returns",
    "extract_shipments",
    "extract_stores",
    "extract_suppliers",
]
