"""
===========================================
Extract - Customers
===========================================
Extracts the customers table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "customers"

EXPECTED_COLUMNS: list[str] = [
    "customer_id", "first_name", "last_name", "gender", "email",
    "phone", "date_of_birth", "city", "state", "country",
    "registration_date", "status",
]


def extract_customers() -> pd.DataFrame:
    """
    Extract all customer records.

    Returns:
        pd.DataFrame: Raw customers data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
