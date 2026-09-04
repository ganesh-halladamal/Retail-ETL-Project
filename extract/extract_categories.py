"""
===========================================
Extract - Categories
===========================================
Extracts the categories table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "categories"

EXPECTED_COLUMNS: list[str] = ["category_id", "category_name", "description"]


def extract_categories() -> pd.DataFrame:
    """
    Extract all product category records.

    Returns:
        pd.DataFrame: Raw categories data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
