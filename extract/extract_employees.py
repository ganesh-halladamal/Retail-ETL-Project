"""
===========================================
Extract - Employees
===========================================
Extracts the employees table from retail_oltp.
"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "employees"

EXPECTED_COLUMNS: list[str] = [
    "employee_id", "store_id", "first_name", "last_name",
    "designation", "salary", "hire_date",
]


def extract_employees() -> pd.DataFrame:
    """
    Extract all employee records.

    Returns:
        pd.DataFrame: Raw employees data

    Raises:
        ExtractionError: If extraction fails
    """
    return extract_table(TABLE_NAME)
