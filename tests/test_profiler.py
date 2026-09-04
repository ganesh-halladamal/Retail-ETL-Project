"""
===========================================
Tests - Profiler Orchestrator
===========================================
Tests for table/column profiling, discovery, loading,
quality scoring, and the ProfilingRun lifecycle.

All tests use in-memory DataFrames — no production
CSV files are required.
"""

import math
from pathlib import Path

import pandas as pd
import pytest

from profiling.column_profiler import (
    detect_type_category,
    profile_column,
    profile_columns,
)
from profiling.quality_rules import DataTypeCategory
from profiling.table_profiler import profile_table, _duplicate_pk_count


# -------------------------------------------------------
# Fixtures
# -------------------------------------------------------

@pytest.fixture()
def clean_customers() -> pd.DataFrame:
    """Minimal customers-shaped DataFrame with no issues."""
    return pd.DataFrame({
        "customer_id": [1, 2, 3],
        "first_name": ["Aarav", "Priya", "Rahul"],
        "email": ["a@example.com", "b@example.com", "c@example.com"],
        "status": ["Active", "Inactive", "Active"],
    })


@pytest.fixture()
def dirty_customers() -> pd.DataFrame:
    """Customers DataFrame with deliberate quality issues."""
    return pd.DataFrame({
        "customer_id": [1, 1, None, 3],           # duplicate + null PK
        "first_name": [" Aarav", "Priya", "Rahul", ""],  # whitespace + empty
        "email": ["bad-email", None, "ok@ex.com", "also@bad"],
        "status": ["Active", "UNKNOWN", "Active", None],
    })


# -------------------------------------------------------
# detect_type_category
# -------------------------------------------------------

class TestDetectTypeCategory:

    def test_integer_series(self):
        s = pd.Series([1, 2, 3])
        assert detect_type_category(s) == DataTypeCategory.INTEGER.value

    def test_float_whole_numbers_detected_as_integer(self):
        s = pd.Series([1.0, 2.0, 3.0])
        assert detect_type_category(s) == DataTypeCategory.INTEGER.value

    def test_float_decimals(self):
        s = pd.Series([1.1, 2.2, 3.3])
        assert detect_type_category(s) == DataTypeCategory.DECIMAL.value

    def test_string_series(self):
        s = pd.Series(["hello", "world"])
        assert detect_type_category(s) == DataTypeCategory.STRING.value

    def test_date_strings(self):
        s = pd.Series(["2024-01-01", "2024-06-15", "2023-12-31"])
        assert detect_type_category(s) == DataTypeCategory.DATE.value

    def test_datetime_strings(self):
        s = pd.Series(["2024-01-01 10:30:00", "2024-06-15 08:00:00"])
        assert detect_type_category(s) == DataTypeCategory.DATETIME.value

    def test_numeric_strings(self):
        s = pd.Series(["1", "2", "3"])
        assert detect_type_category(s) == DataTypeCategory.INTEGER.value

    def test_empty_series(self):
        s = pd.Series([], dtype=object)
        # Empty series should not raise
        result = detect_type_category(s)
        assert result in [member.value for member in DataTypeCategory]


# -------------------------------------------------------
# profile_column
# -------------------------------------------------------

class TestProfileColumn:

    def test_returns_dict_with_required_keys(self, clean_customers):
        result = profile_column(clean_customers["customer_id"], "customers", "customer_id")
        required = [
            "column_name", "row_count", "non_null_count", "null_count",
            "unique_count", "completeness_pct",
        ]
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_no_nulls_in_clean_data(self, clean_customers):
        result = profile_column(clean_customers["customer_id"], "customers", "customer_id")
        assert result["null_count"] == 0
        assert result["completeness_pct"] == 100.0

    def test_null_count_detection(self):
        s = pd.Series([1, None, 3, None])
        result = profile_column(s, "test", "col")
        assert result["null_count"] == 2
        assert result["completeness_pct"] == 50.0

    def test_numeric_stats_present_for_int(self, clean_customers):
        result = profile_column(clean_customers["customer_id"], "customers", "customer_id")
        assert "mean" in result
        assert "min_value" in result

    def test_string_stats_present_for_str(self, clean_customers):
        result = profile_column(clean_customers["first_name"], "customers", "first_name")
        assert "min_length" in result

    def test_type_mismatch_flag(self):
        # Expect INTEGER but supply string values
        s = pd.Series(["hello", "world"])
        result = profile_column(s, "customers", "customer_id")
        assert result["type_matches"] is False

    def test_unique_count(self, clean_customers):
        result = profile_column(clean_customers["status"], "customers", "status")
        assert result["unique_count"] == 2   # Active, Inactive

    def test_profile_columns_returns_one_row_per_column(self, clean_customers):
        df = profile_columns(clean_customers, "customers")
        assert len(df) == len(clean_customers.columns)
        assert "column_name" in df.columns


# -------------------------------------------------------
# profile_table
# -------------------------------------------------------

class TestProfileTable:

    def test_basic_metrics(self, clean_customers):
        result = profile_table(clean_customers, "customers")
        assert result["row_count"] == 3
        assert result["column_count"] == 4
        assert result["duplicate_row_count"] == 0

    def test_duplicate_row_detection(self):
        df = pd.DataFrame({
            "a": [1, 1, 2],
            "b": ["x", "x", "y"],
        })
        result = profile_table(df, "test")
        assert result["duplicate_row_count"] == 1

    def test_completeness_100_percent_clean(self, clean_customers):
        result = profile_table(clean_customers, "customers")
        assert result["completeness_pct"] == 100.0

    def test_completeness_with_nulls(self):
        df = pd.DataFrame({"a": [1, None], "b": ["x", "y"]})
        result = profile_table(df, "test")
        assert result["total_null_values"] == 1

    def test_duplicate_pk_count(self):
        df = pd.DataFrame({"customer_id": [1, 1, 2, 3]})
        assert _duplicate_pk_count(df, "customer_id") == 1

    def test_duplicate_pk_count_no_pk_column(self):
        df = pd.DataFrame({"name": ["a", "b"]})
        assert _duplicate_pk_count(df, "customer_id") == 0

    def test_file_size_defaults_to_zero_without_path(self, clean_customers):
        result = profile_table(clean_customers, "customers", source_path=None)
        assert result["file_size_bytes"] == 0
