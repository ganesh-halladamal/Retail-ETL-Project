"""
===========================================
Extract - Order Items
===========================================
Extracts the order_items table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "order_items"

EXPECTED_COLUMNS: list[str] = [
    "order_item_id", "order_id", "product_id", "quantity",
    "unit_price", "discount_pct", "tax_pct",
    "net_amount", "tax_amount", "line_total",
]


def extract_order_items() -> pd.DataFrame:
    """
    Extract all order line-item records.

    Returns:
        pd.DataFrame: Raw order_items data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
