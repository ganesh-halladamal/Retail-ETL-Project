"""
===========================================
Extract - Orders
===========================================
Extracts the orders table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "orders"

EXPECTED_COLUMNS: list[str] = [
    "order_id", "customer_id", "store_id", "employee_id",
    "order_date", "order_status", "total_amount",
]


def extract_orders() -> pd.DataFrame:
    """
    Extract all order header records.

    Returns:
        pd.DataFrame: Raw orders data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
