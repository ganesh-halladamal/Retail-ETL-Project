"""
===========================================
Extract - Base Extractor
===========================================
Shared extraction logic used by every table
extractor. Keeps the per-table modules thin
and free of duplicated code.
"""

import time
from typing import List, Optional

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from extract.db_connection import DatabaseConnectionError, get_engine
from utils.logger import get_logger

logger = get_logger(__name__)


class ExtractionError(Exception):
    """Raised when a table cannot be extracted."""


def extract_table(table_name: str) -> pd.DataFrame:
    """
    Extract all rows from a source table into a DataFrame.

    Logs start time, end time, row count, duration and status.
    Performs no transformation - the DataFrame mirrors the table.

    Args:
        table_name: Name of the source table to extract

    Returns:
        pd.DataFrame: All rows and columns from the table

    Raises:
        ExtractionError: If the query fails or the connection is unavailable
    """
    start = time.perf_counter()
    logger.info("[%s] Extraction started.", table_name)

    # Table names come from an internal allow-list (TABLES in extractor.py),
    # never from user input, so interpolation here is safe.
    query = text(f"SELECT * FROM {table_name}")  # noqa: S608

    try:
        engine = get_engine()
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)
    except (DatabaseConnectionError, SQLAlchemyError) as exc:
        duration = time.perf_counter() - start
        logger.error(
            "[%s] Extraction FAILED after %.3fs: %s", table_name, duration, exc
        )
        raise ExtractionError(f"Failed to extract '{table_name}': {exc}") from exc

    duration = time.perf_counter() - start
    logger.info(
        "[%s] Extraction SUCCESS | rows=%d | columns=%d | duration=%.3fs",
        table_name, len(df), len(df.columns), duration,
    )
    print(
        f"  [OK] {table_name:<14} rows={len(df):>6}  "
        f"cols={len(df.columns):>2}  time={duration:.3f}s"
    )
    return df


def validate_dataframe(
    table_name: str,
    df: Optional[pd.DataFrame],
    expected_columns: Optional[List[str]] = None,
) -> bool:
    """
    Validate an extracted DataFrame.

    Checks that the frame is not None, has at least one row,
    and contains the expected columns when provided.
    Empty tables are logged as warnings, not errors.

    Args:
        table_name: Table the DataFrame came from
        df: Extracted DataFrame (may be None on failure)
        expected_columns: Columns that must be present, if known

    Returns:
        bool: True if the DataFrame is usable, False otherwise
    """
    if df is None:
        logger.error("[%s] Validation failed: DataFrame is None.", table_name)
        return False

    if df.empty:
        logger.warning("[%s] Validation warning: table is empty (0 rows).", table_name)
        return False

    if not list(df.columns):
        logger.error("[%s] Validation failed: no columns present.", table_name)
        return False

    if expected_columns:
        missing = [col for col in expected_columns if col not in df.columns]
        if missing:
            logger.error(
                "[%s] Validation failed: missing columns %s", table_name, missing
            )
            return False

    logger.info(
        "[%s] Validation passed | rows=%d | columns=%d",
        table_name, len(df), len(df.columns),
    )
    return True
