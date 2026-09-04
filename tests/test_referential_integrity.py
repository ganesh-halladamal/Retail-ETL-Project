"""
===========================================
Tests - Referential Integrity
===========================================
Tests for FK validation, outlier detection,
completeness scoring, and quality score calculation.

All tests use small in-memory DataFrames.
"""

import pandas as pd
import pytest

from profiling.anomaly_detector import compute_iqr_bounds, detect_outliers
from profiling.profiler import (
    DIMENSION_CHECKS,
    _dimension_score,
    calculate_quality_scores,
)
from profiling.quality_engine import (
    reset_check_ids,
    results_to_dataframe,
    run_table_checks,
)
from profiling.quality_rules import CheckType, Severity
from profiling.referential_integrity import (
    _normalise_keys,
    validate_relationship,
    validate_all_relationships,
)


@pytest.fixture(autouse=True)
def reset_ids():
    """Reset check id counter before every test."""
    reset_check_ids()


# -------------------------------------------------------
# Referential integrity validation
# -------------------------------------------------------

class TestForeignKeyValidation:

    @pytest.fixture()
    def fk_products_categories(self):
        from profiling.quality_rules import ForeignKey
        return ForeignKey("products", "category_id", "categories", "category_id")

    def test_all_valid_keys(self, fk_products_categories):
        tables = {
            "categories": pd.DataFrame({"category_id": [1, 2, 3]}),
            "products": pd.DataFrame({"category_id": [1, 2, 3]}),
        }
        metrics = validate_relationship(fk_products_categories, tables)
        assert metrics is not None
        assert metrics["invalid_count"] == 0
        assert metrics["integrity_percentage"] == 100.0
        assert metrics["status"] == "PASS"

    def test_orphan_child_key_detected(self, fk_products_categories):
        tables = {
            "categories": pd.DataFrame({"category_id": [1, 2]}),
            "products": pd.DataFrame({"category_id": [1, 2, 99]}),  # 99 is orphan
        }
        metrics = validate_relationship(fk_products_categories, tables)
        assert metrics is not None
        assert metrics["invalid_count"] == 1
        assert metrics["status"] == "FAIL"

    def test_null_child_keys_not_counted_as_orphans(self, fk_products_categories):
        tables = {
            "categories": pd.DataFrame({"category_id": [1, 2]}),
            "products": pd.DataFrame({"category_id": [1, None, 2]}),
        }
        metrics = validate_relationship(fk_products_categories, tables)
        assert metrics is not None
        assert metrics["invalid_count"] == 0
        assert metrics["null_child_keys"] == 1

    def test_missing_parent_table_returns_none(self, fk_products_categories):
        tables = {
            "products": pd.DataFrame({"category_id": [1, 2]}),
        }
        result = validate_relationship(fk_products_categories, tables)
        assert result is None

    def test_missing_child_table_returns_none(self, fk_products_categories):
        tables = {
            "categories": pd.DataFrame({"category_id": [1, 2]}),
        }
        result = validate_relationship(fk_products_categories, tables)
        assert result is None

    def test_type_coercion_int_vs_float(self, fk_products_categories):
        """Integer IDs vs float IDs (nulls force float) should still match."""
        tables = {
            "categories": pd.DataFrame({"category_id": [1, 2, 3]}),
            "products": pd.DataFrame({"category_id": [1.0, 2.0, 3.0]}),
        }
        metrics = validate_relationship(fk_products_categories, tables)
        assert metrics["invalid_count"] == 0

    def test_validate_all_relationships_returns_dataframe(self):
        tables = {
            "categories": pd.DataFrame({"category_id": [1, 2]}),
            "suppliers": pd.DataFrame({"supplier_id": [1]}),
            "products": pd.DataFrame({
                "category_id": [1, 2], "supplier_id": [1, 1],
            }),
            "stores": pd.DataFrame({"store_id": [1]}),
            "employees": pd.DataFrame({"store_id": [1, 1]}),
            "customers": pd.DataFrame({"customer_id": [1, 2]}),
            "orders": pd.DataFrame({
                "order_id": [1, 2],
                "customer_id": [1, 2], "store_id": [1, 1], "employee_id": [1, 1],
            }),
            "order_items": pd.DataFrame({
                "order_item_id": [1, 2],
                "order_id": [1, 2], "product_id": [1, 1],
            }),
            "payments": pd.DataFrame({"order_id": [1, 2]}),
            "shipments": pd.DataFrame({"order_id": [1]}),
            "returns": pd.DataFrame({"order_item_id": [1]}),
            "inventory": pd.DataFrame({"product_id": [1], "store_id": [1]}),
        }
        df = validate_all_relationships(tables)
        assert not df.empty
        assert "integrity_percentage" in df.columns

    def test_key_normalisation_strips_whitespace(self):
        result = _normalise_keys(pd.Series([" 1 ", "2", " 3"]))
        assert list(result) == ["1", "2", "3"]


# -------------------------------------------------------
# Outlier detection
# -------------------------------------------------------

class TestOutlierDetection:

    def test_no_outliers_in_uniform_data(self):
        df = pd.DataFrame({"unit_price": ["100", "101", "102", "103"]})
        result = detect_outliers(df, "products")
        assert result.empty or result["outlier_count"].sum() == 0

    def test_extreme_value_flagged(self):
        df = pd.DataFrame({"unit_price": ["100", "101", "102", "103", "10000"]})
        result = detect_outliers(df, "products")
        assert not result.empty
        row = result[result["column_name"] == "unit_price"]
        assert row["outlier_count"].values[0] >= 1

    def test_iqr_bounds_correct(self):
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        bounds = compute_iqr_bounds(s)
        assert "q1" in bounds
        assert "q3" in bounds
        assert "iqr" in bounds
        assert bounds["lower_bound"] < bounds["q1"]
        assert bounds["upper_bound"] > bounds["q3"]

    def test_iqr_insufficient_data_returns_empty(self):
        s = pd.Series([1.0, 2.0])
        bounds = compute_iqr_bounds(s)
        assert bounds == {}

    def test_outlier_status_column_present(self):
        df = pd.DataFrame({"salary": ["50000", "55000", "60000", "65000", "1000000"]})
        result = detect_outliers(df, "employees")
        if not result.empty:
            assert "status" in result.columns


# -------------------------------------------------------
# Completeness and quality scoring
# -------------------------------------------------------

class TestQualityScoring:

    def _make_results(self, check_type: str, total: int, failed: int) -> pd.DataFrame:
        """Helper: build a minimal results frame for scoring tests."""
        passed = total - failed
        return pd.DataFrame([{
            "table_name": "test_table",
            "check_type": check_type,
            "total_records": total,
            "passed_records": passed,
            "failed_records": failed,
            "failure_percentage": failed / total * 100 if total else 0,
            "severity": Severity.HIGH.value,
        }])

    def test_perfect_completeness_score(self):
        results = self._make_results(CheckType.NULL_VALUE.value, 100, 0)
        score = _dimension_score(results, DIMENSION_CHECKS["completeness"])
        assert score == 100.0

    def test_partial_completeness_score(self):
        results = self._make_results(CheckType.NULL_VALUE.value, 100, 10)
        score = _dimension_score(results, DIMENSION_CHECKS["completeness"])
        assert score == 90.0

    def test_calculate_quality_scores_returns_one_row_per_table(self):
        customers_results = run_table_checks(
            pd.DataFrame({"customer_id": [1, 2], "first_name": ["A", "B"],
                          "email": ["a@b.com", "c@d.com"]}),
            "customers",
        )
        products_results = run_table_checks(
            pd.DataFrame({"product_id": [1], "unit_price": ["99.99"],
                          "cost_price": ["50.00"]}),
            "products",
        )
        all_results = results_to_dataframe(customers_results + products_results)
        scores = calculate_quality_scores(all_results)
        assert set(scores["table_name"]) == {"customers", "products"}
        assert "overall_quality_score" in scores.columns

    def test_overall_score_between_0_and_100(self):
        df = pd.DataFrame({
            "customer_id": [1, 1],
            "first_name": [None, "B"],
            "email": ["bad", "ok@ok.com"],
        })
        results = results_to_dataframe(run_table_checks(df, "customers"))
        scores = calculate_quality_scores(results)
        row = scores[scores["table_name"] == "customers"]
        score = row["overall_quality_score"].values[0]
        assert 0.0 <= score <= 100.0

    def test_empty_results_returns_empty_scores(self):
        scores = calculate_quality_scores(pd.DataFrame())
        assert scores.empty
