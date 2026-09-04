"""
===========================================
Profiling - Quality Engine
===========================================
Executes every metadata-driven quality check against
a raw table and returns standardised QualityResult
records.

Checks implemented here:
    nulls, empty strings, whitespace
    duplicate rows, duplicate/null/invalid primary keys
    data type mismatches
    date validity, future dates, out-of-range dates
    numeric negatives, zeros and range violations
    string whitespace, multiple spaces, excessive length
    email and phone format
    categorical domain membership
    declarative business rules (single and cross-table)

Read-only: input DataFrames are never mutated.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from profiling.column_profiler import _null_like_mask, detect_type_category
from profiling.quality_rules import (
    BUSINESS_RULES,
    CATEGORICAL_VALUES,
    CROSS_TABLE_DATE_RULES,
    DATE_COLUMNS,
    EMAIL_COLUMNS,
    EMAIL_PATTERN,
    EXPECTED_DTYPES,
    FUTURE_DATE_COLUMNS,
    MAX_STRING_LENGTH,
    MIN_REASONABLE_BIRTH_DATE,
    MIN_REASONABLE_DATE,
    NULLABLE_BY_DESIGN,
    NULL_SEVERITY_OPTIONAL,
    NULL_SEVERITY_PRIMARY_KEY,
    NULL_SEVERITY_REQUIRED,
    NUMERIC_RULES,
    PHONE_ALLOWED_PATTERN,
    PHONE_COLUMNS,
    PHONE_MAX_DIGITS,
    PHONE_MIN_DIGITS,
    PRIMARY_KEYS,
    REQUIRED_COLUMNS,
    SAMPLE_LIMIT,
    CheckType,
    QualityResult,
    Severity,
    severity_for,
)
from utils.logger import get_profiling_logger

logger = get_profiling_logger(__name__)


# Sequential counter for check_id generation
_check_counter: Dict[str, int] = {"n": 0}


def _next_check_id() -> str:
    """Return the next sequential check identifier (CHK00001, ...)."""
    _check_counter["n"] += 1
    return f"CHK{_check_counter['n']:05d}"


def reset_check_ids() -> None:
    """Reset the check id counter. Used by tests for deterministic ids."""
    _check_counter["n"] = 0


def _samples(series: pd.Series, mask: pd.Series) -> str:
    """
    Build a comma separated sample of failing values.

    Args:
        series: Column being checked
        mask: Boolean mask of failing rows

    Returns:
        str: Up to SAMPLE_LIMIT failing values as text
    """
    if not mask.any():
        return ""
    values = series[mask].head(SAMPLE_LIMIT).astype(str).tolist()
    return ", ".join(values)


def _make_result(
    table: str,
    column: str,
    check_type: str,
    description: str,
    total: int,
    failed_mask: pd.Series,
    rule_id: str = "",
    severity: Optional[str] = None,
    samples: Optional[str] = None,
    series: Optional[pd.Series] = None,
) -> QualityResult:
    """
    Build a QualityResult from a failing-row mask.

    Args:
        table: Table name
        column: Column name (or comma separated list)
        check_type: CheckType value
        description: Human readable check description
        total: Total records evaluated
        failed_mask: Boolean mask, True where the row fails
        rule_id: Business rule id when applicable
        severity: Override for the configured severity
        samples: Pre-built sample string
        series: Column used to derive samples when not supplied

    Returns:
        QualityResult: Standardised result record
    """
    failed = int(failed_mask.sum()) if len(failed_mask) else 0
    passed = total - failed
    sample_text = samples
    if sample_text is None:
        sample_text = _samples(series, failed_mask) if series is not None else ""

    return QualityResult(
        check_id=_next_check_id(),
        rule_id=rule_id,
        table_name=table,
        column_name=column,
        check_type=check_type,
        description=description,
        total_records=total,
        passed_records=passed,
        failed_records=failed,
        failure_percentage=round(failed / total * 100, 2) if total else 0.0,
        severity=severity or severity_for(check_type),
        sample_values=sample_text,
    )


def check_nulls(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Detect null and null-equivalent values in every column.

    Severity depends on the column's role: CRITICAL for primary
    keys, HIGH for required columns, LOW for optional ones.
    Columns nullable by design are skipped.

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: One result per column checked
    """
    results: List[QualityResult] = []
    total = len(df)
    primary_key = PRIMARY_KEYS.get(table, "")
    required = set(REQUIRED_COLUMNS.get(table, []))
    by_design = set(NULLABLE_BY_DESIGN.get(table, []))

    for column in df.columns:
        if column in by_design:
            continue

        mask = _null_like_mask(df[column])
        if column == primary_key:
            severity = NULL_SEVERITY_PRIMARY_KEY
            check_type = CheckType.NULL_PRIMARY_KEY.value
        elif column in required:
            severity = NULL_SEVERITY_REQUIRED
            check_type = CheckType.NULL_VALUE.value
        else:
            severity = NULL_SEVERITY_OPTIONAL
            check_type = CheckType.NULL_VALUE.value

        results.append(
            _make_result(
                table, column, check_type,
                f"Column '{column}' must not contain null or blank values.",
                total, mask, severity=severity, series=df[column],
            )
        )
    return results


def check_duplicate_rows(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Detect fully duplicated rows.

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: Single result for the table
    """
    mask = df.duplicated(keep="first")
    return [
        _make_result(
            table, "<all columns>", CheckType.DUPLICATE_ROW.value,
            "Table must not contain fully duplicated rows.",
            len(df), mask,
            samples=f"{int(mask.sum())} duplicated row(s)" if mask.any() else "",
        )
    ]


def check_primary_key(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Validate the primary key: no duplicates, no nulls, and no
    invalid values (non-numeric, negative or zero identifiers).

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: Duplicate, null and invalid-value results
    """
    primary_key = PRIMARY_KEYS.get(table, "")
    if not primary_key or primary_key not in df.columns:
        logger.warning(
            "[%s] Primary key '%s' not found; skipping PK validation.",
            table, primary_key,
        )
        return []

    results: List[QualityResult] = []
    total = len(df)
    series = df[primary_key]

    # Duplicate keys
    dup_mask = series.duplicated(keep="first")
    results.append(
        _make_result(
            table, primary_key, CheckType.DUPLICATE_PRIMARY_KEY.value,
            f"Primary key '{primary_key}' must be unique.",
            total, dup_mask, series=series,
        )
    )

    # Null keys
    null_mask = _null_like_mask(series)
    results.append(
        _make_result(
            table, primary_key, CheckType.NULL_PRIMARY_KEY.value,
            f"Primary key '{primary_key}' must not be null.",
            total, null_mask, series=series,
        )
    )

    # Invalid keys: unparseable, negative or zero
    numeric = pd.to_numeric(series, errors="coerce")
    invalid_mask = (~null_mask) & (numeric.isna() | (numeric <= 0))
    results.append(
        _make_result(
            table, primary_key, CheckType.INVALID_PRIMARY_KEY.value,
            f"Primary key '{primary_key}' must be a positive integer.",
            total, invalid_mask, series=series,
        )
    )
    return results


def check_data_types(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Compare each column's detected type against the expected type
    from EXPECTED_DTYPES and flag mismatches.

    A mismatch is reported as affecting every row, because the
    problem is the column's type rather than individual values.

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: One result per column with a known expectation
    """
    expectations = EXPECTED_DTYPES.get(table, {})
    if not expectations:
        return []

    results: List[QualityResult] = []
    total = len(df)

    for column, expected in expectations.items():
        if column not in df.columns:
            continue

        detected = detect_type_category(df[column])
        # INTEGER stored as DECIMAL is acceptable (nulls force float dtype)
        compatible = detected == expected or (
            expected == "INTEGER" and detected == "DECIMAL"
        )
        mask = pd.Series([not compatible] * total, index=df.index)

        results.append(
            _make_result(
                table, column, CheckType.DATA_TYPE_MISMATCH.value,
                f"Column '{column}' expected {expected}, detected {detected}.",
                total, mask,
                samples="" if compatible else f"expected={expected}, detected={detected}",
            )
        )
    return results


def check_dates(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Validate date columns for parseability, future dates and
    implausibly early dates.

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: Validity, future-date and range results
    """
    date_cols = DATE_COLUMNS.get(table, [])
    if not date_cols:
        return []

    results: List[QualityResult] = []
    total = len(df)
    now = pd.Timestamp.now()
    future_cols = set(FUTURE_DATE_COLUMNS.get(table, []))

    for column in date_cols:
        if column not in df.columns:
            continue

        series = df[column]
        null_mask = _null_like_mask(series)
        parsed = pd.to_datetime(series, errors="coerce", format="mixed")

        # Unparseable but not null -> invalid date
        invalid_mask = (~null_mask) & parsed.isna()
        results.append(
            _make_result(
                table, column, CheckType.INVALID_DATE.value,
                f"Column '{column}' must contain parseable dates.",
                total, invalid_mask, series=series,
            )
        )

        # Future dates
        if column in future_cols:
            future_mask = parsed.notna() & (parsed > now)
            results.append(
                _make_result(
                    table, column, CheckType.FUTURE_DATE.value,
                    f"Column '{column}' must not contain future dates.",
                    total, future_mask, series=series,
                )
            )

        # Implausibly early dates
        floor = (
            MIN_REASONABLE_BIRTH_DATE
            if column == "date_of_birth"
            else MIN_REASONABLE_DATE
        )
        early_mask = parsed.notna() & (parsed < pd.Timestamp(floor))
        results.append(
            _make_result(
                table, column, CheckType.DATE_OUT_OF_RANGE.value,
                f"Column '{column}' must not contain dates before {floor}.",
                total, early_mask, series=series,
            )
        )
    return results


def check_numerics(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Validate numeric columns against their configured NumericRule:
    negative values, disallowed zeros, and range bounds.

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: One result per applicable constraint
    """
    rules = [rule for rule in NUMERIC_RULES if rule.table == table]
    if not rules:
        return []

    results: List[QualityResult] = []
    total = len(df)

    for rule in rules:
        if rule.column not in df.columns:
            continue

        series = df[rule.column]
        values = pd.to_numeric(series, errors="coerce")

        if not rule.allow_negative:
            mask = values.notna() & (values < 0)
            results.append(
                _make_result(
                    table, rule.column, CheckType.NEGATIVE_VALUE.value,
                    f"Column '{rule.column}' must not be negative.",
                    total, mask, series=series,
                )
            )

        if not rule.allow_zero:
            mask = values.notna() & (values == 0)
            results.append(
                _make_result(
                    table, rule.column, CheckType.ZERO_VALUE.value,
                    f"Column '{rule.column}' must not be zero.",
                    total, mask, series=series,
                )
            )

        if rule.min_value is not None or rule.max_value is not None:
            low = rule.min_value if rule.min_value is not None else float("-inf")
            high = rule.max_value if rule.max_value is not None else float("inf")
            mask = values.notna() & ((values < low) | (values > high))
            results.append(
                _make_result(
                    table, rule.column, CheckType.BUSINESS_RULE.value,
                    f"Column '{rule.column}' must be between {low} and {high}.",
                    total, mask, series=series,
                    severity=Severity.MEDIUM.value,
                )
            )
    return results


def check_strings(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Inspect string columns for whitespace and length problems.

    Reports leading/trailing whitespace, multiple consecutive
    spaces, empty or whitespace-only values, and values exceeding
    the configured maximum length. Nothing is cleaned.

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: Whitespace, empty and length results
    """
    results: List[QualityResult] = []
    total = len(df)

    for column in df.columns:
        if df[column].dtype != object:
            continue

        series = df[column]
        # Compare raw text against its stripped form without mutating source
        raw = series.fillna("").astype(str)
        stripped = raw.str.strip()
        populated = series.notna()

        ws_mask = populated & (raw != stripped)
        results.append(
            _make_result(
                table, column,
                CheckType.LEADING_OR_TRAILING_WHITESPACE.value,
                f"Column '{column}' must not have leading or trailing whitespace.",
                total, ws_mask,
                samples=", ".join(
                    f"'{value}'" for value in raw[ws_mask].head(SAMPLE_LIMIT)
                ) if ws_mask.any() else "",
            )
        )

        multi_mask = populated & stripped.str.contains(r"\s{2,}", regex=True, na=False)
        results.append(
            _make_result(
                table, column, CheckType.MULTIPLE_SPACES.value,
                f"Column '{column}' must not contain consecutive spaces.",
                total, multi_mask, series=series,
            )
        )

        empty_mask = populated & (stripped == "")
        results.append(
            _make_result(
                table, column, CheckType.EMPTY_STRING.value,
                f"Column '{column}' must not contain empty or blank strings.",
                total, empty_mask,
                samples=f"{int(empty_mask.sum())} blank value(s)" if empty_mask.any() else "",
            )
        )

        limit = MAX_STRING_LENGTH.get(column, MAX_STRING_LENGTH["default"])
        long_mask = populated & (stripped.str.len() > limit)
        results.append(
            _make_result(
                table, column, CheckType.EXCESSIVE_LENGTH.value,
                f"Column '{column}' must not exceed {limit} characters.",
                total, long_mask,
                samples=", ".join(
                    str(length) for length in stripped[long_mask].str.len().head(SAMPLE_LIMIT)
                ) if long_mask.any() else "",
            )
        )
    return results


def check_emails(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Validate email columns against EMAIL_PATTERN.

    Nulls are excluded here; they are reported by the null checks.

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: One result per email column
    """
    columns = EMAIL_COLUMNS.get(table, [])
    results: List[QualityResult] = []
    total = len(df)

    for column in columns:
        if column not in df.columns:
            continue

        series = df[column]
        populated = ~_null_like_mask(series)
        text = series.fillna("").astype(str).str.strip()
        matches = text.str.match(EMAIL_PATTERN, na=False)
        mask = populated & ~matches

        results.append(
            _make_result(
                table, column, CheckType.INVALID_EMAIL.value,
                f"Column '{column}' must contain valid email addresses.",
                total, mask, series=series,
            )
        )
    return results


def check_phones(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Validate phone columns: allowed characters and digit count
    within the configured range. Country-agnostic by design.

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: One result per phone column
    """
    columns = PHONE_COLUMNS.get(table, [])
    results: List[QualityResult] = []
    total = len(df)

    for column in columns:
        if column not in df.columns:
            continue

        series = df[column]
        populated = ~_null_like_mask(series)
        text = series.fillna("").astype(str).str.strip()

        allowed = text.str.match(PHONE_ALLOWED_PATTERN, na=False)
        digit_count = text.str.replace(r"\D", "", regex=True).str.len()
        in_range = (digit_count >= PHONE_MIN_DIGITS) & (digit_count <= PHONE_MAX_DIGITS)
        mask = populated & (~allowed | ~in_range)

        results.append(
            _make_result(
                table, column, CheckType.INVALID_PHONE.value,
                f"Column '{column}' must contain {PHONE_MIN_DIGITS}-"
                f"{PHONE_MAX_DIGITS} digits and no invalid characters.",
                total, mask, series=series,
            )
        )
    return results


def check_categories(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Verify categorical columns contain only expected values.

    Comparison is case-insensitive and whitespace-trimmed so that
    casing differences surface as whitespace/format issues rather
    than invalid categories.

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: One result per categorical column
    """
    domains = CATEGORICAL_VALUES.get(table, {})
    results: List[QualityResult] = []
    total = len(df)

    for column, allowed_values in domains.items():
        if column not in df.columns:
            continue

        series = df[column]
        populated = ~_null_like_mask(series)
        normalised = series.fillna("").astype(str).str.strip().str.casefold()
        allowed = {value.casefold() for value in allowed_values}
        mask = populated & ~normalised.isin(allowed)

        results.append(
            _make_result(
                table, column, CheckType.INVALID_CATEGORY.value,
                f"Column '{column}' must be one of: {', '.join(allowed_values)}.",
                total, mask, series=series,
            )
        )
    return results


def get_category_distribution(
    df: pd.DataFrame,
    table: str,
) -> pd.DataFrame:
    """
    Build a frequency distribution for the table's categorical columns.

    Args:
        df: Table data
        table: Table name

    Returns:
        pd.DataFrame: table_name, column_name, value, frequency,
            percentage and is_expected flag
    """
    domains = CATEGORICAL_VALUES.get(table, {})
    rows: List[Dict[str, Any]] = []
    total = len(df)

    for column, allowed_values in domains.items():
        if column not in df.columns:
            continue

        allowed = {value.casefold() for value in allowed_values}
        counts = df[column].value_counts(dropna=False)
        for value, frequency in counts.items():
            label = "<NULL>" if pd.isna(value) else str(value)
            rows.append({
                "table_name": table,
                "column_name": column,
                "value": label,
                "frequency": int(frequency),
                "percentage": round(int(frequency) / total * 100, 2) if total else 0.0,
                "is_expected": (
                    False if pd.isna(value)
                    else str(value).strip().casefold() in allowed
                ),
            })
    return pd.DataFrame(rows)


def check_business_rules(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Execute the declarative business rules configured for a table.

    Each rule predicate returns True for passing rows, so the
    failing mask is its negation.

    Args:
        df: Table data
        table: Table name

    Returns:
        List[QualityResult]: One result per rule evaluated
    """
    rules = [rule for rule in BUSINESS_RULES if rule.table == table]
    results: List[QualityResult] = []
    total = len(df)

    for rule in rules:
        missing = [col for col in rule.columns if col not in df.columns]
        if missing:
            logger.warning(
                "[%s] %s skipped; missing columns: %s",
                table, rule.rule_id, ", ".join(missing),
            )
            continue

        try:
            passing = rule.predicate(df)
        except (TypeError, ValueError) as exc:
            logger.error("[%s] %s failed to evaluate: %s", table, rule.rule_id, exc)
            continue

        failed_mask = ~passing.fillna(True)
        sample_series = df[rule.columns[0]]
        results.append(
            _make_result(
                table, rule.column_label, CheckType.BUSINESS_RULE.value,
                rule.description, total, failed_mask,
                rule_id=rule.rule_id, severity=rule.severity,
                series=sample_series,
            )
        )
    return results


def check_cross_table_dates(
    tables: Dict[str, pd.DataFrame],
) -> List[QualityResult]:
    """
    Validate date ordering rules that span two tables, joining the
    child to its parent on the configured key.

    Args:
        tables: All loaded tables, keyed by name

    Returns:
        List[QualityResult]: One result per applicable rule
    """
    results: List[QualityResult] = []

    for rule in CROSS_TABLE_DATE_RULES:
        child = tables.get(rule.child_table)
        parent = tables.get(rule.parent_table)
        if child is None or parent is None:
            continue

        needed_child = {rule.child_key, rule.child_date_column}
        needed_parent = {rule.parent_key, rule.parent_date_column}
        if not needed_child <= set(child.columns):
            continue
        if not needed_parent <= set(parent.columns):
            continue

        # Read-only join on copies of just the needed columns
        parent_dates = parent[[rule.parent_key, rule.parent_date_column]]
        merged = child[[rule.child_key, rule.child_date_column]].merge(
            parent_dates,
            left_on=rule.child_key,
            right_on=rule.parent_key,
            how="left",
        )
        child_date = pd.to_datetime(
            merged[rule.child_date_column], errors="coerce", format="mixed"
        )
        parent_date = pd.to_datetime(
            merged[rule.parent_date_column], errors="coerce", format="mixed"
        )
        comparable = child_date.notna() & parent_date.notna()
        failed_mask = comparable & (child_date < parent_date)

        results.append(
            _make_result(
                rule.child_table,
                f"{rule.child_date_column} vs {rule.parent_table}.{rule.parent_date_column}",
                CheckType.DATE_SEQUENCE.value,
                rule.description, len(child), failed_mask,
                rule_id=rule.rule_id, severity=rule.severity,
                samples=", ".join(
                    str(value) for value in merged.loc[failed_mask, rule.child_date_column]
                    .head(SAMPLE_LIMIT).astype(str)
                ) if failed_mask.any() else "",
            )
        )
    return results


def run_table_checks(df: pd.DataFrame, table: str) -> List[QualityResult]:
    """
    Run every single-table quality check against one table.

    Args:
        df: Table data (not modified)
        table: Table name

    Returns:
        List[QualityResult]: All results for the table
    """
    logger.info("[%s] Quality checks started.", table)

    results: List[QualityResult] = []
    results.extend(check_nulls(df, table))
    results.extend(check_duplicate_rows(df, table))
    results.extend(check_primary_key(df, table))
    results.extend(check_data_types(df, table))
    results.extend(check_dates(df, table))
    results.extend(check_numerics(df, table))
    results.extend(check_strings(df, table))
    results.extend(check_emails(df, table))
    results.extend(check_phones(df, table))
    results.extend(check_categories(df, table))
    results.extend(check_business_rules(df, table))

    failed = sum(1 for result in results if not result.passed)
    logger.info(
        "[%s] Quality checks completed | checks=%d | failed=%d",
        table, len(results), failed,
    )
    return results


def results_to_dataframe(results: List[QualityResult]) -> pd.DataFrame:
    """
    Convert QualityResult records into a DataFrame.

    Args:
        results: Results to convert

    Returns:
        pd.DataFrame: One row per result, with stable column order
    """
    columns = [
        "check_id", "rule_id", "table_name", "column_name", "check_type",
        "description", "total_records", "passed_records", "failed_records",
        "failure_percentage", "severity", "sample_values", "execution_timestamp",
    ]
    if not results:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame([result.to_dict() for result in results], columns=columns)
