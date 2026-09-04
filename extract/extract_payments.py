"""
===========================================
Extract - Payments
===========================================
Extracts the payments table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "payments"

EXPECTED_COLUMNS: list[str] = [
    "payment_id", "order_id", "payment_method",
    "payment_status", "payment_date", "amount_paid",
]


def extract_payments() -> pd.DataFrame:
    """
    Extract all payment records.

    Returns:
        pd.DataFrame: Raw payments data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
