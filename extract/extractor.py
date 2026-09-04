"""
===========================================
Extract - Master Extractor
===========================================
Orchestrates extraction of every source table into
Pandas DataFrames, validates them, and saves raw
CSV snapshots to data/raw/.

No transformation is performed here, and nothing is
written to the warehouse - extraction only.
"""

import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import pandas as pd

from extract import (
    extract_categories,
    extract_customers,
    extract_employees,
    extract_inventory,
    extract_order_items,
    extract_orders,
    extract_payments,
    extract_products,
    extract_returns,
    extract_shipments,
    extract_stores,
    extract_suppliers,
)
from extract.base_extractor import ExtractionError, validate_dataframe
from extract.db_connection import dispose_engine, test_connection
from utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
RAW_DATA_DIR: Path = PROJECT_ROOT / "data" / "raw"
CSV_ENCODING: str = "utf-8"

# Extraction registry: table name -> (extract function, expected columns)
# Ordered parent-first so raw snapshots read naturally.
ExtractorFn = Callable[[], pd.DataFrame]

TABLE_REGISTRY: Dict[str, Tuple[ExtractorFn, List[str]]] = {
    "categories": (
        extract_categories.extract_categories,
        extract_categories.EXPECTED_COLUMNS,
    ),
    "suppliers": (
        extract_suppliers.extract_suppliers,
        extract_suppliers.EXPECTED_COLUMNS,
    ),
    "stores": (
        extract_stores.extract_stores,
        extract_stores.EXPECTED_COLUMNS,
    ),
    "products": (
        extract_products.extract_products,
        extract_products.EXPECTED_COLUMNS,
    ),
    "employees": (
        extract_employees.extract_employees,
        extract_employees.EXPECTED_COLUMNS,
    ),
    "customers": (
        extract_customers.extract_customers,
        extract_customers.EXPECTED_COLUMNS,
    ),
    "inventory": (
        extract_inventory.extract_inventory,
        extract_inventory.EXPECTED_COLUMNS,
    ),
    "orders": (
        extract_orders.extract_orders,
        extract_orders.EXPECTED_COLUMNS,
    ),
    "order_items": (
        extract_order_items.extract_order_items,
        extract_order_items.EXPECTED_COLUMNS,
    ),
    "payments": (
        extract_payments.extract_payments,
        extract_payments.EXPECTED_COLUMNS,
    ),
    "shipments": (
        extract_shipments.extract_shipments,
        extract_shipments.EXPECTED_COLUMNS,
    ),
    "returns": (
        extract_returns.extract_returns,
        extract_returns.EXPECTED_COLUMNS,
    ),
}


def save_to_csv(table_name: str, df: pd.DataFrame) -> Optional[Path]:
    """
    Save a DataFrame as a UTF-8 CSV snapshot in data/raw/.

    Args:
        table_name: Source table name (becomes the file stem)
        df: DataFrame to persist

    Returns:
        Optional[Path]: Path to the written file, or None if the write failed
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RAW_DATA_DIR / f"{table_name}.csv"

    try:
        df.to_csv(output_path, index=False, encoding=CSV_ENCODING)
    except OSError as exc:
        logger.error("[%s] Failed to write CSV to %s: %s", table_name, output_path, exc)
        return None

    logger.info("[%s] Saved %d rows to %s", table_name, len(df), output_path)
    return output_path


def extract_all(save_csv: bool = True) -> Dict[str, pd.DataFrame]:
    """
    Extract every source table into a dictionary of DataFrames.

    A failure on one table is logged and skipped; the remaining
    tables are still extracted so the pipeline never halts early.

    Args:
        save_csv: When True, write each DataFrame to data/raw/<table>.csv

    Returns:
        Dict[str, pd.DataFrame]: Mapping of table name to extracted DataFrame.
            Tables that failed extraction are absent from the mapping.
    """
    job_start = time.perf_counter()
    logger.info("=" * 60)
    logger.info("EXTRACTION JOB STARTED | tables=%d", len(TABLE_REGISTRY))

    data: Dict[str, pd.DataFrame] = {}
    failed: List[str] = []
    empty: List[str] = []

    if not test_connection():
        logger.error("EXTRACTION JOB ABORTED | source database unreachable.")
        return data

    for table_name, (extract_fn, expected_columns) in TABLE_REGISTRY.items():
        try:
            df = extract_fn()
        except ExtractionError as exc:
            logger.error("[%s] Skipped due to error: %s", table_name, exc)
            print(f"  [FAIL] {table_name:<14} {exc}")
            failed.append(table_name)
            continue

        if not validate_dataframe(table_name, df, expected_columns):
            # Empty tables are legitimate; keep them but flag in the summary
            if df is not None and df.empty:
                empty.append(table_name)
                data[table_name] = df
                if save_csv:
                    save_to_csv(table_name, df)
                continue
            failed.append(table_name)
            continue

        data[table_name] = df
        if save_csv:
            save_to_csv(table_name, df)

    duration = time.perf_counter() - job_start
    _log_job_summary(data, failed, empty, duration)
    return data


def _log_job_summary(
    data: Dict[str, pd.DataFrame],
    failed: List[str],
    empty: List[str],
    duration: float,
) -> None:
    """
    Write the end-of-job summary to the log file.

    Args:
        data: Successfully extracted DataFrames
        failed: Table names that could not be extracted
        empty: Table names that returned zero rows
        duration: Total job duration in seconds
    """
    total_rows = sum(len(df) for df in data.values())
    status = "SUCCESS" if not failed else "COMPLETED WITH ERRORS"

    logger.info("-" * 60)
    logger.info(
        "EXTRACTION JOB %s | extracted=%d | failed=%d | empty=%d | "
        "total_rows=%d | duration=%.3fs",
        status, len(data), len(failed), len(empty), total_rows, duration,
    )
    if failed:
        logger.error("Failed tables: %s", ", ".join(failed))
    if empty:
        logger.warning("Empty tables: %s", ", ".join(empty))
    logger.info("=" * 60)


def get_extraction_summary(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Build a tabular summary of an extraction run.

    Args:
        data: Mapping returned by extract_all()

    Returns:
        pd.DataFrame: One row per table with row and column counts
    """
    rows = [
        {
            "table": table_name,
            "rows": len(df),
            "columns": len(df.columns),
            "status": "EMPTY" if df.empty else "OK",
        }
        for table_name, df in data.items()
    ]
    return pd.DataFrame(rows, columns=["table", "rows", "columns", "status"])


def close() -> None:
    """Release the connection pool once extraction is finished."""
    dispose_engine()
