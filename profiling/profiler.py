"""
===========================================
Profiling - Profiler Orchestrator
===========================================
Discovers raw CSV extracts, loads them read-only,
runs every profiling and quality component, and
computes completeness and quality scores.

Guarantee: files under data/raw/ are opened in read
mode only. No profiling function writes to the input
directory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from profiling.anomaly_detector import detect_outliers, outliers_to_quality_results
from profiling.column_profiler import profile_columns
from profiling.quality_engine import (
    check_cross_table_dates,
    get_category_distribution,
    results_to_dataframe,
    run_table_checks,
)
from profiling.quality_rules import (
    EXPECTED_TABLES,
    SCORE_WEIGHTS,
    CheckType,
    QualityResult,
    SEVERITY_ORDER,
    Severity,
)
from profiling.referential_integrity import (
    relationships_to_quality_results,
    validate_all_relationships,
)
from profiling.table_profiler import profile_table
from utils.logger import get_profiling_logger

logger = get_profiling_logger(__name__)

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
DEFAULT_INPUT_DIR: Path = PROJECT_ROOT / "data" / "raw"
DEFAULT_OUTPUT_DIR: Path = PROJECT_ROOT / "data" / "profiling"
CSV_ENCODING: str = "utf-8"


@dataclass
class ProfilingRun:
    """Complete output of a profiling run."""

    table_profiles: pd.DataFrame = field(default_factory=pd.DataFrame)
    column_profiles: Dict[str, pd.DataFrame] = field(default_factory=dict)
    quality_results: pd.DataFrame = field(default_factory=pd.DataFrame)
    referential_integrity: pd.DataFrame = field(default_factory=pd.DataFrame)
    outliers: pd.DataFrame = field(default_factory=pd.DataFrame)
    category_distribution: pd.DataFrame = field(default_factory=pd.DataFrame)
    quality_scores: pd.DataFrame = field(default_factory=pd.DataFrame)
    summary: Dict[str, Any] = field(default_factory=dict)
    tables_discovered: List[str] = field(default_factory=list)
    tables_missing: List[str] = field(default_factory=list)
    load_errors: Dict[str, str] = field(default_factory=dict)


def discover_csv_files(input_dir: Path = DEFAULT_INPUT_DIR) -> Dict[str, Path]:
    """
    Find raw CSV extracts in the input directory.

    Table names are derived from file stems, so customers.csv
    becomes the 'customers' table.

    Args:
        input_dir: Directory holding the raw CSV files

    Returns:
        Dict[str, Path]: Mapping of table name to file path
    """
    if not input_dir.exists():
        logger.error("Input directory does not exist: %s", input_dir)
        return {}

    discovered = {
        path.stem: path
        for path in sorted(input_dir.glob("*.csv"))
        if path.is_file()
    }
    logger.info(
        "Discovered %d CSV file(s) in %s: %s",
        len(discovered), input_dir, ", ".join(discovered) or "none",
    )
    return discovered


def load_tables(
    csv_files: Dict[str, Path],
) -> tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
    """
    Load CSV extracts into DataFrames, read-only.

    Every column is read as object dtype so that the profiler can
    judge the raw text itself: whitespace, blank strings and
    unparseable values all survive intact instead of being silently
    coerced by the CSV reader.

    Args:
        csv_files: Mapping of table name to file path

    Returns:
        tuple: (loaded tables, load errors keyed by table name)
    """
    tables: Dict[str, pd.DataFrame] = {}
    errors: Dict[str, str] = {}

    for table_name, path in csv_files.items():
        try:
            df = pd.read_csv(
                path,
                dtype=str,
                keep_default_na=True,
                encoding=CSV_ENCODING,
                skipinitialspace=False,
            )
        except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
            logger.error("[%s] Failed to load %s: %s", table_name, path, exc)
            errors[table_name] = str(exc)
            continue

        tables[table_name] = df
        logger.info(
            "[%s] Table loaded | rows=%d | columns=%d | source=%s",
            table_name, len(df), len(df.columns), path.name,
        )

    return tables, errors


# Which check types contribute to each quality dimension.
# POTENTIAL_OUTLIER is deliberately excluded: outliers are for review,
# not defects, so they must not depress the score.
DIMENSION_CHECKS: Dict[str, set] = {
    "completeness": {
        CheckType.NULL_VALUE.value,
        CheckType.NULL_PRIMARY_KEY.value,
    },
    "uniqueness": {
        CheckType.DUPLICATE_ROW.value,
        CheckType.DUPLICATE_PRIMARY_KEY.value,
    },
    "validity": {
        CheckType.DATA_TYPE_MISMATCH.value,
        CheckType.INVALID_PRIMARY_KEY.value,
        CheckType.INVALID_DATE.value,
        CheckType.FUTURE_DATE.value,
        CheckType.DATE_OUT_OF_RANGE.value,
        CheckType.NEGATIVE_VALUE.value,
        CheckType.ZERO_VALUE.value,
        CheckType.INVALID_EMAIL.value,
        CheckType.INVALID_PHONE.value,
        CheckType.INVALID_CATEGORY.value,
        CheckType.EMPTY_STRING.value,
        CheckType.EXCESSIVE_LENGTH.value,
    },
    "consistency": {
        CheckType.BUSINESS_RULE.value,
        CheckType.DATE_SEQUENCE.value,
        CheckType.LEADING_OR_TRAILING_WHITESPACE.value,
        CheckType.MULTIPLE_SPACES.value,
    },
    "referential_integrity": {
        CheckType.FOREIGN_KEY.value,
    },
}


def _dimension_score(results: pd.DataFrame, check_types: set) -> float:
    """
    Score one quality dimension as a record-weighted pass rate.

    Args:
        results: Quality results for a single table
        check_types: Check types belonging to the dimension

    Returns:
        float: Score from 0-100; 100.0 when the dimension has no checks
    """
    subset = results[results["check_type"].isin(check_types)]
    if subset.empty:
        return 100.0

    total = int(subset["total_records"].sum())
    passed = int(subset["passed_records"].sum())
    if total == 0:
        return 100.0
    return round(passed / total * 100, 2)


def calculate_quality_scores(quality_results: pd.DataFrame) -> pd.DataFrame:
    """
    Compute per-table dimension scores and a weighted overall score.

    The formula is documented in docs/data_quality_rules.md:

        overall = sum(dimension_score * dimension_weight)

    Args:
        quality_results: All quality results across tables

    Returns:
        pd.DataFrame: One row per table with dimension and overall scores
    """
    columns = [
        "table_name", "completeness", "uniqueness", "validity",
        "consistency", "referential_integrity", "overall_quality_score",
        "total_checks", "failed_checks",
    ]
    if quality_results.empty:
        return pd.DataFrame(columns=columns)

    rows: List[Dict[str, Any]] = []
    for table_name, table_results in quality_results.groupby("table_name"):
        scores = {
            dimension: _dimension_score(table_results, check_types)
            for dimension, check_types in DIMENSION_CHECKS.items()
        }
        overall = sum(
            scores[dimension] * weight
            for dimension, weight in SCORE_WEIGHTS.items()
        )
        rows.append({
            "table_name": table_name,
            **scores,
            "overall_quality_score": round(overall, 2),
            "total_checks": len(table_results),
            "failed_checks": int((table_results["failed_records"] > 0).sum()),
        })

    return pd.DataFrame(rows, columns=columns).sort_values("table_name")


def build_summary(run: ProfilingRun) -> Dict[str, Any]:
    """
    Build the headline profiling summary.

    Args:
        run: Populated ProfilingRun

    Returns:
        Dict[str, Any]: Summary counts, severity breakdown and overall score
    """
    results = run.quality_results
    failed = results[results["failed_records"] > 0] if not results.empty else results

    severity_counts = {level.value: 0 for level in Severity}
    if not failed.empty:
        counts = failed["severity"].value_counts().to_dict()
        severity_counts.update({key: int(value) for key, value in counts.items()})

    total_records = (
        int(run.table_profiles["row_count"].sum())
        if not run.table_profiles.empty else 0
    )
    total_columns = (
        int(run.table_profiles["column_count"].sum())
        if not run.table_profiles.empty else 0
    )
    overall_score = (
        round(float(run.quality_scores["overall_quality_score"].mean()), 2)
        if not run.quality_scores.empty else 0.0
    )

    return {
        "tables_profiled": len(run.tables_discovered),
        "tables_expected": len(EXPECTED_TABLES),
        "tables_missing": run.tables_missing,
        "total_records": total_records,
        "total_columns": total_columns,
        "total_quality_checks": len(results),
        "passed_checks": len(results) - len(failed) if not results.empty else 0,
        "failed_checks": len(failed),
        "critical_issues": severity_counts[Severity.CRITICAL.value],
        "high_issues": severity_counts[Severity.HIGH.value],
        "medium_issues": severity_counts[Severity.MEDIUM.value],
        "low_issues": severity_counts[Severity.LOW.value],
        "info_issues": severity_counts[Severity.INFO.value],
        "relationships_checked": len(run.referential_integrity),
        "relationships_failed": (
            int((run.referential_integrity["status"] == "FAIL").sum())
            if not run.referential_integrity.empty else 0
        ),
        "overall_quality_score": overall_score,
        "load_errors": run.load_errors,
    }


def run_profiling(
    input_dir: Path = DEFAULT_INPUT_DIR,
    only_table: Optional[str] = None,
) -> ProfilingRun:
    """
    Execute the full profiling and quality assessment.

    Steps: discover CSVs, load them read-only, profile tables and
    columns, run quality checks, validate primary and foreign keys,
    evaluate business rules, detect outliers, and score each table.

    Args:
        input_dir: Directory containing raw CSV extracts
        only_table: Restrict profiling to a single table when given

    Returns:
        ProfilingRun: All profiling artefacts and the summary
    """
    logger.info("=" * 60)
    logger.info("PROFILING START | input_dir=%s | table=%s",
                input_dir, only_table or "ALL")

    run = ProfilingRun()
    csv_files = discover_csv_files(input_dir)

    if only_table:
        csv_files = {
            name: path for name, path in csv_files.items() if name == only_table
        }
        if not csv_files:
            logger.error("Table '%s' not found in %s", only_table, input_dir)
            run.summary = build_summary(run)
            return run

    tables, run.load_errors = load_tables(csv_files)
    run.tables_discovered = sorted(tables)
    run.tables_missing = (
        [] if only_table
        else [name for name in EXPECTED_TABLES if name not in tables]
    )

    if run.tables_missing:
        logger.warning(
            "Expected tables missing from extract: %s",
            ", ".join(run.tables_missing),
        )

    if not tables:
        logger.error("No tables loaded; nothing to profile.")
        run.summary = build_summary(run)
        return run

    run = _profile_loaded_tables(run, tables, csv_files, only_table)
    logger.info("PROFILING COMPLETE | score=%.2f%%",
                run.summary.get("overall_quality_score", 0.0))
    logger.info("=" * 60)
    return run


def _profile_loaded_tables(
    run: ProfilingRun,
    tables: Dict[str, pd.DataFrame],
    csv_files: Dict[str, Path],
    only_table: Optional[str],
) -> ProfilingRun:
    """
    Profile every loaded table and assemble the run artefacts.

    Args:
        run: Run being populated
        tables: Loaded tables, keyed by name
        csv_files: Source paths, keyed by table name
        only_table: Set when profiling a single table

    Returns:
        ProfilingRun: The populated run
    """
    table_profiles: List[Dict[str, Any]] = []
    all_results: List[QualityResult] = []
    outlier_frames: List[pd.DataFrame] = []
    category_frames: List[pd.DataFrame] = []

    for table_name, df in tables.items():
        table_profiles.append(
            profile_table(df, table_name, csv_files.get(table_name))
        )
        run.column_profiles[table_name] = profile_columns(df, table_name)
        all_results.extend(run_table_checks(df, table_name))

        outliers = detect_outliers(df, table_name)
        if not outliers.empty:
            outlier_frames.append(outliers)
            all_results.extend(outliers_to_quality_results(outliers))

        categories = get_category_distribution(df, table_name)
        if not categories.empty:
            category_frames.append(categories)

    # Cross-table checks need every table, so they are skipped for
    # single-table runs where the counterpart may not be loaded.
    if only_table is None:
        run.referential_integrity = validate_all_relationships(tables)
        all_results.extend(
            relationships_to_quality_results(run.referential_integrity)
        )
        all_results.extend(check_cross_table_dates(tables))
    else:
        logger.info(
            "Single-table run; referential integrity and cross-table "
            "date rules skipped."
        )

    run.table_profiles = pd.DataFrame(table_profiles)
    run.quality_results = _sort_by_severity(results_to_dataframe(all_results))
    run.outliers = (
        pd.concat(outlier_frames, ignore_index=True)
        if outlier_frames else pd.DataFrame()
    )
    run.category_distribution = (
        pd.concat(category_frames, ignore_index=True)
        if category_frames else pd.DataFrame()
    )
    run.quality_scores = calculate_quality_scores(run.quality_results)
    run.summary = build_summary(run)
    return run


def _sort_by_severity(results: pd.DataFrame) -> pd.DataFrame:
    """
    Order results with failures first, most severe at the top.

    Args:
        results: Quality results

    Returns:
        pd.DataFrame: Sorted results without the temporary sort keys
    """
    if results.empty:
        return results

    ordered = results.assign(
        _has_failures=(results["failed_records"] > 0).astype(int),
        _severity_rank=results["severity"].map(SEVERITY_ORDER).fillna(99),
    ).sort_values(
        ["_has_failures", "_severity_rank", "failed_records"],
        ascending=[False, True, False],
    )
    return ordered.drop(columns=["_has_failures", "_severity_rank"])
