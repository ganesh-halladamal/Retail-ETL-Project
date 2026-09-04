"""
===========================================
Extract - Suppliers
===========================================
Extracts the suppliers table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "suppliers"

EXPECTED_COLUMNS: list[str] = [
    "supplier_id", "supplier_name", "contact_person",
    "email", "phone", "city", "country",
]


def extract_suppliers() -> pd.DataFrame:
    """
    Extract all supplier records.

    Returns:
        pd.DataFrame: Raw suppliers data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
