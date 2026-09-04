"""
===========================================
Profiling - Column Profiler
===========================================
Per-column statistics for a raw DataFrame.

Numeric statistics are computed only for numeric
columns, string-length statistics only for string
columns, and date statistics only for date columns.

Read-only: never mutates the input DataFrame.
"""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from profiling.quality_rules import (
    DataTypeCategory,
    NULL_LIKE_TOKENS,
    EXPECTED_DTYPES,
)
from utils.logger import get_profiling_logger

logger = get_profiling_logger(__name__)


def detect_type_category(series: pd.Series) -> str:
    """
    Infer the logical data type category of a Series.

    Detection order matters: booleans before integers, integers
    before decimals, and datetime parsing is attempted on object
    columns before falling back to STRING.

    Args:
        series: Column to inspect

    Returns:
        str: A DataTypeCategory value
    """
    if pd.api.types.is_bool_dtype(series):
        return DataTypeCategory.BOOLEAN.value
    if pd.api.types.is_integer_dtype(series):
        return DataTypeCategory.INTEGER.value
    if pd.api.types.is_float_dtype(series):
        # Whole-valued floats are usually integer columns carrying nulls
        non_null = series.dropna()
        if not non_null.empty and np.all(np.mod(non_null.values, 1) == 0):
            return DataTypeCategory.INTEGER.value
        return DataTypeCategory.DECIMAL.value
    if pd.api.types.is_datetime64_any_dtype(series):
        return DataTypeCategory.DATETIME.value
    return _detect_object_type(series)


def _detect_object_type(series: pd.Series) -> str:
    """
    Classify an object-dtype column as INTEGER, DECIMAL, DATE,
    DATETIME or STRING based on how cleanly its values parse.

    Args:
        series: Object-dtype column

    Returns:
        str: A DataTypeCategory value
    """
    non_null = series.dropna().astype(str).str.strip()
    non_null = non_null[~non_null.isin(NULL_LIKE_TOKENS)]

    if non_null.empty:
        return DataTypeCategory.UNKNOWN.value

    # Numeric?
    numeric = pd.to_numeric(non_null, errors="coerce")
    if numeric.notna().all():
        if np.all(np.mod(numeric.dropna().values, 1) == 0):
            return DataTypeCategory.INTEGER.value
        return DataTypeCategory.DECIMAL.value

    # Date / datetime? Only trust a full parse to avoid false positives.
    parsed = pd.to_datetime(non_null, errors="coerce", format="mixed")
    if parsed.notna().all():
        has_time = (
            (parsed.dt.hour != 0)
            | (parsed.dt.minute != 0)
            | (parsed.dt.second != 0)
        ).any()
        return (
            DataTypeCategory.DATETIME.value
            if has_time
            else DataTypeCategory.DATE.value
        )

    return DataTypeCategory.STRING.value


def _null_like_mask(series: pd.Series) -> pd.Series:
    """
    Return a mask of values that are null or null-equivalent
    (empty string, whitespace only, or a NULL-like token).

    Args:
        series: Column to inspect

    Returns:
        pd.Series: Boolean mask, True where the value is null-like
    """
    mask = series.isna()
    if series.dtype == object:
        as_text = series.astype(str).str.strip()
        mask = mask | as_text.isin(NULL_LIKE_TOKENS)
    return mask


def _pct(part: int, whole: int) -> float:
    """Return part/whole as a percentage rounded to 2dp, 0.0 when whole is 0."""
    if whole == 0:
        return 0.0
    return round(part / whole * 100, 2)


def _numeric_stats(series: pd.Series) -> Dict[str, Any]:
    """Compute min/max/mean/median/std for a numeric-like column."""
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return {}
    return {
        "min_value": round(float(values.min()), 4),
        "max_value": round(float(values.max()), 4),
        "mean": round(float(values.mean()), 4),
        "median": round(float(values.median()), 4),
        "std_dev": round(float(values.std()), 4) if len(values) > 1 else 0.0,
    }


def _string_stats(series: pd.Series) -> Dict[str, Any]:
    """Compute min/max/avg string length for a string column."""
    text = series.dropna().astype(str)
    if text.empty:
        return {}
    lengths = text.str.len()
    return {
        "min_length": int(lengths.min()),
        "max_length": int(lengths.max()),
        "avg_length": round(float(lengths.mean()), 2),
        "min_value": str(text.min()),
        "max_value": str(text.max()),
    }


def _date_stats(series: pd.Series) -> Dict[str, Any]:
    """Compute earliest/latest values for a date or datetime column."""
    parsed = pd.to_datetime(series, errors="coerce", format="mixed").dropna()
    if parsed.empty:
        return {}
    return {
        "min_value": parsed.min().isoformat(),
        "max_value": parsed.max().isoformat(),
        "invalid_date_count": int(
            pd.to_datetime(series, errors="coerce", format="mixed").isna().sum()
            - series.isna().sum()
        ),
    }


def profile_column(
    series: pd.Series,
    table_name: str = "",
    column_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Profile a single column.

    Args:
        series: Column data
        table_name: Owning table, used to look up the expected type
        column_name: Column name; defaults to the Series name

    Returns:
        Dict[str, Any]: Column profile with counts, percentages and
            type-appropriate statistics
    """
    name = column_name if column_name is not None else str(series.name)
    total = len(series)

    null_mask = _null_like_mask(series)
    null_count = int(null_mask.sum())
    non_null_count = total - null_count

    # Distinct count over genuinely populated values only
    populated = series[~null_mask]
    unique_count = int(populated.nunique(dropna=True))

    detected = detect_type_category(series)
    expected = EXPECTED_DTYPES.get(table_name, {}).get(name, "")

    empty_count = 0
    if series.dtype == object:
        as_text = series.fillna("").astype(str)
        empty_count = int((as_text.str.strip() == "").sum())

    profile: Dict[str, Any] = {
        "table_name": table_name,
        "column_name": name,
        "pandas_dtype": str(series.dtype),
        "detected_type": detected,
        "expected_type": expected,
        "type_matches": (not expected) or expected == detected,
        "row_count": total,
        "non_null_count": non_null_count,
        "null_count": null_count,
        "null_percentage": _pct(null_count, total),
        "empty_count": empty_count,
        "empty_percentage": _pct(empty_count, total),
        "unique_count": unique_count,
        "unique_percentage": _pct(unique_count, non_null_count),
        "duplicate_count": max(non_null_count - unique_count, 0),
        "completeness_pct": _pct(non_null_count, total),
    }
    profile.update(_stats_for_type(series, detected))
    return profile


def _stats_for_type(series: pd.Series, detected: str) -> Dict[str, Any]:
    """
    Dispatch to the statistics function appropriate for the
    detected type category.

    Args:
        series: Column data
        detected: DataTypeCategory value

    Returns:
        Dict[str, Any]: Type-specific statistics
    """
    numeric_types = {
        DataTypeCategory.INTEGER.value,
        DataTypeCategory.DECIMAL.value,
    }
    date_types = {
        DataTypeCategory.DATE.value,
        DataTypeCategory.DATETIME.value,
    }

    if detected in numeric_types:
        return _numeric_stats(series)
    if detected in date_types:
        return _date_stats(series)
    if detected == DataTypeCategory.STRING.value:
        return _string_stats(series)
    return {}


def profile_columns(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """
    Profile every column in a DataFrame.

    Args:
        df: Raw table data (not modified)
        table_name: Table the DataFrame came from

    Returns:
        pd.DataFrame: One row per column
    """
    profiles: List[Dict[str, Any]] = [
        profile_column(df[column], table_name, column)
        for column in df.columns
    ]
    logger.info("[%s] Profiled %d columns.", table_name, len(profiles))
    return pd.DataFrame(profiles)
