"""
===========================================
Profiling - Referential Integrity
===========================================
Validates the metadata-driven foreign key
relationships between raw CSV extracts.

Because profiling runs against flat files rather
than the live database, relationships that the
database enforces can still be broken here by a
partial or stale extract - which is exactly what
this module is designed to catch.

Read-only: input DataFrames are never mutated.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from profiling.column_profiler import _null_like_mask
from profiling.quality_rules import (
    FOREIGN_KEYS,
    SAMPLE_LIMIT,
    CheckType,
    ForeignKey,
    QualityResult,
    Severity,
)
from profiling.quality_engine import _make_result
from utils.logger import get_profiling_logger

logger = get_profiling_logger(__name__)


def validate_relationship(
    foreign_key: ForeignKey,
    tables: Dict[str, pd.DataFrame],
) -> Optional[Dict[str, Any]]:
    """
    Validate one foreign key relationship.

    Null child keys are not counted as orphans; they are reported
    by the null checks instead.

    Args:
        foreign_key: Relationship to validate
        tables: All loaded tables, keyed by name

    Returns:
        Optional[Dict[str, Any]]: Relationship metrics, or None when
            either side is missing from the extract
    """
    child = tables.get(foreign_key.child_table)
    parent = tables.get(foreign_key.parent_table)

    if child is None or parent is None:
        logger.warning(
            "%s skipped; missing table in extract.", foreign_key.label
        )
        return None

    if foreign_key.child_column not in child.columns:
        logger.warning(
            "%s skipped; child column absent.", foreign_key.label
        )
        return None

    if foreign_key.parent_column not in parent.columns:
        logger.warning(
            "%s skipped; parent column absent.", foreign_key.label
        )
        return None

    return _compute_relationship_metrics(foreign_key, child, parent)


def _compute_relationship_metrics(
    foreign_key: ForeignKey,
    child: pd.DataFrame,
    parent: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Compute valid/invalid/orphan counts for a relationship.

    Keys are normalised to strings on both sides so that an integer
    column on one side and a float-with-nulls column on the other
    still match correctly.

    Args:
        foreign_key: Relationship being validated
        child: Child table
        parent: Parent table

    Returns:
        Dict[str, Any]: Relationship metrics
    """
    child_keys = child[foreign_key.child_column]
    parent_keys = parent[foreign_key.parent_column]

    null_mask = _null_like_mask(child_keys)
    comparable = child_keys[~null_mask]

    parent_values = set(_normalise_keys(parent_keys.dropna()))
    child_normalised = _normalise_keys(comparable)

    valid_mask = child_normalised.isin(parent_values)
    valid_count = int(valid_mask.sum())
    invalid_count = int((~valid_mask).sum())
    checked = valid_count + invalid_count

    orphan_values = child_normalised[~valid_mask]
    integrity_pct = round(valid_count / checked * 100, 2) if checked else 100.0

    return {
        "parent_table": foreign_key.parent_table,
        "parent_column": foreign_key.parent_column,
        "child_table": foreign_key.child_table,
        "child_column": foreign_key.child_column,
        "parent_count": len(parent),
        "child_count": len(child),
        "null_child_keys": int(null_mask.sum()),
        "checked_count": checked,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "orphan_count": invalid_count,
        "integrity_percentage": integrity_pct,
        "status": "PASS" if invalid_count == 0 else "FAIL",
        "severity": (
            Severity.INFO.value if invalid_count == 0 else foreign_key.severity
        ),
        "sample_orphans": ", ".join(
            orphan_values.head(SAMPLE_LIMIT).astype(str).tolist()
        ),
    }


def _normalise_keys(series: pd.Series) -> pd.Series:
    """
    Normalise key values for comparison across dtypes.

    Numeric keys are compared as integers where possible so that
    5, 5.0 and '5' are treated as the same key.

    Args:
        series: Key column

    Returns:
        pd.Series: Normalised string keys
    """
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().all():
        return numeric.astype("Int64").astype(str)
    return series.astype(str).str.strip()


def validate_all_relationships(
    tables: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Validate every configured foreign key relationship.

    Args:
        tables: All loaded tables, keyed by name

    Returns:
        pd.DataFrame: One row per relationship with integrity metrics
    """
    columns = [
        "parent_table", "parent_column", "child_table", "child_column",
        "parent_count", "child_count", "null_child_keys", "checked_count",
        "valid_count", "invalid_count", "orphan_count",
        "integrity_percentage", "status", "severity", "sample_orphans",
    ]

    rows: List[Dict[str, Any]] = []
    for foreign_key in FOREIGN_KEYS:
        metrics = validate_relationship(foreign_key, tables)
        if metrics is None:
            continue
        rows.append(metrics)
        if metrics["invalid_count"]:
            logger.warning(
                "%s | orphans=%d | integrity=%.2f%%",
                foreign_key.label,
                metrics["invalid_count"],
                metrics["integrity_percentage"],
            )
        else:
            logger.info(
                "%s | integrity=100%% | rows=%d",
                foreign_key.label, metrics["child_count"],
            )

    logger.info("Validated %d relationships.", len(rows))
    return pd.DataFrame(rows, columns=columns)


def relationships_to_quality_results(
    integrity_df: pd.DataFrame,
) -> List[QualityResult]:
    """
    Convert relationship metrics into standard QualityResult records
    so foreign key findings appear alongside all other checks.

    Args:
        integrity_df: Output of validate_all_relationships()

    Returns:
        List[QualityResult]: One result per relationship
    """
    results: List[QualityResult] = []

    for row in integrity_df.itertuples(index=False):
        checked = int(row.checked_count)
        invalid = int(row.invalid_count)
        mask = pd.Series([True] * invalid + [False] * (checked - invalid))

        results.append(
            _make_result(
                row.child_table,
                row.child_column,
                CheckType.FOREIGN_KEY.value,
                f"{row.child_table}.{row.child_column} must reference an existing "
                f"{row.parent_table}.{row.parent_column}.",
                checked,
                mask,
                severity=row.severity,
                samples=row.sample_orphans,
            )
        )
    return results
