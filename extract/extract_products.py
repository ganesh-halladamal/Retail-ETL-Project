"""
===========================================
Extract - Products
===========================================
Extracts the products table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "products"

EXPECTED_COLUMNS: list[str] = [
    "product_id", "category_id", "supplier_id", "product_name",
    "brand", "unit_price", "cost_price", "created_date", "status",
]


def extract_products() -> pd.DataFrame:
    """
    Extract all product catalog records.

    Returns:
        pd.DataFrame: Raw products data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
