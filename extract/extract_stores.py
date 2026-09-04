"""
===========================================
Extract - Stores
===========================================
Extracts the stores table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "stores"

EXPECTED_COLUMNS: list[str] = [
    "store_id", "store_name", "city", "state",
    "manager_name", "opened_date",
]


def extract_stores() -> pd.DataFrame:
    """
    Extract all retail store records.

    Returns:
        pd.DataFrame: Raw stores data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
