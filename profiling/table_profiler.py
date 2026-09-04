"""
===========================================
Profiling - Table Profiler
===========================================
Table-level metrics for a raw DataFrame:
row/column counts, duplicates, null totals,
file size and completeness.

Read-only: never mutates the input DataFrame.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from profiling.column_profiler import _null_like_mask, _pct
from profiling.quality_rules import PRIMARY_KEYS
from utils.logger import get_profiling_logger

logger = get_profiling_logger(__name__)


def profile_table(
    df: pd.DataFrame,
    table_name: str,
    source_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Profile a table as a whole.

    Args:
        df: Raw table data (not modified)
        table_name: Table name
        source_path: Originating CSV, used to report file size

    Returns:
        Dict[str, Any]: Table-level profile
    """
    row_count = len(df)
    column_count = len(df.columns)
    total_cells = row_count * column_count

    duplicate_rows = int(df.duplicated(keep="first").sum())

    # Null-like mask across the whole frame, computed column-wise
    null_mask = pd.DataFrame(
        {col: _null_like_mask(df[col]) for col in df.columns},
        index=df.index,
    ) if column_count else pd.DataFrame(index=df.index)

    total_nulls = int(null_mask.to_numpy().sum()) if column_count else 0
    empty_rows = int(null_mask.all(axis=1).sum()) if column_count else 0

    primary_key = PRIMARY_KEYS.get(table_name, "")
    duplicate_pk_count = _duplicate_pk_count(df, primary_key)

    profile: Dict[str, Any] = {
        "table_name": table_name,
        "row_count": row_count,
        "column_count": column_count,
        "file_size_bytes": _file_size(source_path),
        "file_size_kb": round(_file_size(source_path) / 1024, 2),
        "duplicate_row_count": duplicate_rows,
        "duplicate_row_percentage": _pct(duplicate_rows, row_count),
        "empty_row_count": empty_rows,
        "primary_key": primary_key,
        "duplicate_pk_count": duplicate_pk_count,
        "total_cells": total_cells,
        "total_null_values": total_nulls,
        "total_null_percentage": _pct(total_nulls, total_cells),
        "total_populated_values": total_cells - total_nulls,
        "completeness_pct": _pct(total_cells - total_nulls, total_cells),
        "profiled_at": datetime.now().isoformat(timespec="seconds"),
    }
    logger.info(
        "[%s] Table profile | rows=%d | cols=%d | dup_rows=%d | nulls=%d",
        table_name, row_count, column_count, duplicate_rows, total_nulls,
    )
    return profile


def _file_size(source_path: Optional[Path]) -> int:
    """
    Return the size of a file in bytes, or 0 when unavailable.

    Args:
        source_path: Path to inspect

    Returns:
        int: Size in bytes
    """
    if source_path is None:
        return 0
    try:
        return source_path.stat().st_size
    except OSError:
        return 0


def _duplicate_pk_count(df: pd.DataFrame, primary_key: str) -> int:
    """
    Count duplicated primary key values.

    Args:
        df: Table data
        primary_key: Primary key column name (may be empty/absent)

    Returns:
        int: Number of rows carrying a duplicated key value
    """
    if not primary_key or primary_key not in df.columns:
        return 0
    return int(df[primary_key].duplicated(keep="first").sum())


def profile_tables(
    tables: Dict[str, pd.DataFrame],
    source_paths: Optional[Dict[str, Path]] = None,
) -> pd.DataFrame:
    """
    Profile every loaded table.

    Args:
        tables: Mapping of table name to DataFrame
        source_paths: Optional mapping of table name to source CSV path

    Returns:
        pd.DataFrame: One row per table
    """
    paths = source_paths or {}
    profiles = [
        profile_table(df, name, paths.get(name))
        for name, df in tables.items()
    ]
    return pd.DataFrame(profiles)
