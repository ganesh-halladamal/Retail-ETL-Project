"""
===========================================
Extract - Inventory
===========================================
Extracts the inventory table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "inventory"

EXPECTED_COLUMNS: list[str] = [
    "inventory_id", "product_id", "store_id",
    "stock_quantity", "last_updated",
]


def extract_inventory() -> pd.DataFrame:
    """
    Extract all inventory (stock per product per store) records.

    Returns:
        pd.DataFrame: Raw inventory data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
