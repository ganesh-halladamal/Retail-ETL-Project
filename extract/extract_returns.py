"""
===========================================
Extract - Returns
===========================================
Extracts the returns table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "returns"

EXPECTED_COLUMNS: list[str] = [
    "return_id", "order_item_id", "return_reason",
    "return_date", "refund_amount",
]


def extract_returns() -> pd.DataFrame:
    """
    Extract all product return records.

    Returns:
        pd.DataFrame: Raw returns data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
