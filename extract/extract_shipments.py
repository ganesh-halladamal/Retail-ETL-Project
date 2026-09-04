"""
===========================================
Extract - Shipments
===========================================
Extracts the shipments table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "shipments"

EXPECTED_COLUMNS: list[str] = [
    "shipment_id", "order_id", "shipping_partner", "tracking_number",
    "shipment_date", "delivery_date", "shipment_status",
]


def extract_shipments() -> pd.DataFrame:
    """
    Extract all shipment records.

    Returns:
        pd.DataFrame: Raw shipments data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
