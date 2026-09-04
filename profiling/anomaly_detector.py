"""
===========================================
Profiling - Anomaly Detector
===========================================
IQR-based outlier detection for numeric columns.

Outliers are reported as POTENTIAL_OUTLIER at INFO
severity, never as errors. A high-value order or a
premium product price is a legitimate outlier, so
these findings are for human review rather than
automatic correction.

Read-only: input DataFrames are never mutated.
"""

from typing import Any, Dict, List

import pandas as pd

from profiling.quality_engine import _make_result
from profiling.quality_rules import (
    IQR_MULTIPLIER,
    OUTLIER_COLUMNS,
    SAMPLE_LIMIT,
    CheckType,
    QualityResult,
    Severity,
)
from utils.logger import get_profiling_logger

logger = get_profiling_logger(__name__)


def compute_iqr_bounds(series: pd.Series) -> Dict[str, float]:
    """
    Compute IQR statistics and outlier bounds for a numeric column.

    Args:
        series: Column to analyse

    Returns:
        Dict[str, float]: q1, q3, iqr, lower_bound and upper_bound.
            Empty dict when there is insufficient numeric data.
    """
    values = pd.to_numeric(series, errors="coerce").dropna()
    if len(values) < 4:
        return {}

    q1 = float(values.quantile(0.25))
    q3 = float(values.quantile(0.75))
    iqr = q3 - q1

    return {
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "iqr": round(iqr, 4),
        "lower_bound": round(q1 - IQR_MULTIPLIER * iqr, 4),
        "upper_bound": round(q3 + IQR_MULTIPLIER * iqr, 4),
    }


def detect_outliers(df: pd.DataFrame, table: str) -> pd.DataFrame:
    """
    Detect IQR outliers in the table's configured numeric columns.

    Args:
        df: Table data (not modified)
        table: Table name

    Returns:
        pd.DataFrame: One row per column analysed, with bounds and counts
    """
    columns = OUTLIER_COLUMNS.get(table, [])
    schema = [
        "table_name", "column_name", "q1", "q3", "iqr",
        "lower_bound", "upper_bound", "total_values", "outlier_count",
        "outlier_percentage", "low_outliers", "high_outliers",
        "min_outlier", "max_outlier", "sample_outliers", "status",
    ]

    rows: List[Dict[str, Any]] = []
    for column in columns:
        if column not in df.columns:
            continue

        bounds = compute_iqr_bounds(df[column])
        if not bounds:
            logger.info(
                "[%s] %s skipped for outliers; insufficient numeric data.",
                table, column,
            )
            continue

        values = pd.to_numeric(df[column], errors="coerce")
        populated = values.notna()
        low_mask = populated & (values < bounds["lower_bound"])
        high_mask = populated & (values > bounds["upper_bound"])
        outlier_mask = low_mask | high_mask

        total_values = int(populated.sum())
        outlier_count = int(outlier_mask.sum())
        outliers = values[outlier_mask]

        rows.append({
            "table_name": table,
            "column_name": column,
            **bounds,
            "total_values": total_values,
            "outlier_count": outlier_count,
            "outlier_percentage": (
                round(outlier_count / total_values * 100, 2) if total_values else 0.0
            ),
            "low_outliers": int(low_mask.sum()),
            "high_outliers": int(high_mask.sum()),
            "min_outlier": float(outliers.min()) if outlier_count else None,
            "max_outlier": float(outliers.max()) if outlier_count else None,
            "sample_outliers": ", ".join(
                outliers.head(SAMPLE_LIMIT).astype(str).tolist()
            ),
            "status": (
                CheckType.POTENTIAL_OUTLIER.value if outlier_count else "NONE"
            ),
        })

    if rows:
        logger.info("[%s] Outlier scan covered %d column(s).", table, len(rows))
    return pd.DataFrame(rows, columns=schema)


def outliers_to_quality_results(
    outlier_df: pd.DataFrame,
) -> List[QualityResult]:
    """
    Convert outlier metrics into QualityResult records at INFO
    severity, flagged POTENTIAL_OUTLIER rather than as failures.

    Args:
        outlier_df: Output of detect_outliers()

    Returns:
        List[QualityResult]: One result per column analysed
    """
    results: List[QualityResult] = []

    for row in outlier_df.itertuples(index=False):
        total = int(row.total_values)
        count = int(row.outlier_count)
        mask = pd.Series([True] * count + [False] * (total - count))

        results.append(
            _make_result(
                row.table_name,
                row.column_name,
                CheckType.POTENTIAL_OUTLIER.value,
                f"Values outside [{row.lower_bound}, {row.upper_bound}] "
                f"(IQR x {IQR_MULTIPLIER}) are potential outliers and need review.",
                total,
                mask,
                severity=Severity.INFO.value,
                samples=row.sample_outliers,
            )
        )
    return results
