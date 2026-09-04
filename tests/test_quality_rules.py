"""
===========================================
Tests - Quality Engine Checks
===========================================
Tests for null, duplicate, PK, date, numeric,
string, email, phone, category, and business-rule
checks.

All tests use small in-memory DataFrames.
"""

from datetime import date

import pandas as pd
import pytest

from profiling.quality_engine import (
    check_business_rules,
    check_categories,
    check_dates,
    check_duplicate_rows,
    check_emails,
    check_numerics,
    check_phones,
    check_primary_key,
    check_nulls,
    check_strings,
    reset_check_ids,
    results_to_dataframe,
    run_table_checks,
)
from profiling.quality_rules import CheckType, Severity


@pytest.fixture(autouse=True)
def reset_ids():
    """Reset check id counter before every test for deterministic ids."""
    reset_check_ids()


# -------------------------------------------------------
# Null checks
# -------------------------------------------------------

class TestCheckNulls:

    def test_no_nulls(self):
        df = pd.DataFrame({"customer_id": [1, 2], "first_name": ["A", "B"]})
        results = check_nulls(df, "customers")
        assert all(r.passed for r in results)

    def test_null_in_required_column(self):
        df = pd.DataFrame({"customer_id": [1, 2], "first_name": ["A", None]})
        results = check_nulls(df, "customers")
        failed = [r for r in results if not r.passed]
        assert any(r.column_name == "first_name" for r in failed)

    def test_primary_key_null_is_critical(self):
        df = pd.DataFrame({"customer_id": [1, None]})
        results = check_nulls(df, "customers")
        pk_result = next(
            (r for r in results if r.column_name == "customer_id"), None
        )
        assert pk_result is not None
        assert pk_result.severity == Severity.CRITICAL.value
        assert pk_result.failed_records == 1

    def test_blank_string_treated_as_null(self):
        df = pd.DataFrame({
            "customer_id": [1],
            "first_name": ["   "],  # whitespace only
        })
        results = check_nulls(df, "customers")
        failed = [r for r in results if r.column_name == "first_name" and not r.passed]
        assert len(failed) == 1

    def test_nullable_by_design_column_skipped(self):
        df = pd.DataFrame({
            "category_id": [1],
            "category_name": ["Electronics"],
            "description": [None],  # nullable by design
        })
        results = check_nulls(df, "categories")
        desc_results = [r for r in results if r.column_name == "description"]
        assert len(desc_results) == 0


# -------------------------------------------------------
# Duplicate checks
# -------------------------------------------------------

class TestCheckDuplicateRows:

    def test_no_duplicates(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        results = check_duplicate_rows(df, "test")
        assert results[0].passed

    def test_detects_duplicate(self):
        df = pd.DataFrame({"a": [1, 1, 2]})
        results = check_duplicate_rows(df, "test")
        assert results[0].failed_records == 1


# -------------------------------------------------------
# Primary key checks
# -------------------------------------------------------

class TestCheckPrimaryKey:

    def test_clean_primary_key(self):
        df = pd.DataFrame({"customer_id": [1, 2, 3]})
        results = check_primary_key(df, "customers")
        assert all(r.passed for r in results)

    def test_duplicate_primary_key(self):
        df = pd.DataFrame({"customer_id": [1, 1, 2]})
        results = check_primary_key(df, "customers")
        dup = next(r for r in results
                   if r.check_type == CheckType.DUPLICATE_PRIMARY_KEY.value)
        assert dup.failed_records == 1

    def test_null_primary_key(self):
        df = pd.DataFrame({"customer_id": [1, None]})
        results = check_primary_key(df, "customers")
        null_res = next(r for r in results
                        if r.check_type == CheckType.NULL_PRIMARY_KEY.value)
        assert null_res.failed_records == 1
        assert null_res.severity == Severity.CRITICAL.value

    def test_negative_primary_key(self):
        df = pd.DataFrame({"customer_id": [1, -1]})
        results = check_primary_key(df, "customers")
        invalid = next(r for r in results
                       if r.check_type == CheckType.INVALID_PRIMARY_KEY.value)
        assert invalid.failed_records == 1

    def test_zero_primary_key(self):
        df = pd.DataFrame({"customer_id": [1, 0]})
        results = check_primary_key(df, "customers")
        invalid = next(r for r in results
                       if r.check_type == CheckType.INVALID_PRIMARY_KEY.value)
        assert invalid.failed_records == 1

    def test_missing_pk_column_returns_empty(self):
        df = pd.DataFrame({"some_column": [1, 2]})
        results = check_primary_key(df, "customers")
        assert results == []


# -------------------------------------------------------
# Date checks
# -------------------------------------------------------

class TestCheckDates:

    def test_valid_dates_pass(self):
        df = pd.DataFrame({
            "customer_id": [1],
            "date_of_birth": ["1990-05-14"],
            "registration_date": ["2022-01-15"],
        })
        results = check_dates(df, "customers")
        failed = [r for r in results if not r.passed]
        assert len(failed) == 0

    def test_future_date_flagged(self):
        df = pd.DataFrame({
            "customer_id": [1],
            "date_of_birth": ["2099-01-01"],
            "registration_date": ["2022-01-15"],
        })
        results = check_dates(df, "customers")
        future = [r for r in results
                  if r.check_type == CheckType.FUTURE_DATE.value
                  and r.column_name == "date_of_birth"]
        assert any(r.failed_records > 0 for r in future)

    def test_invalid_date_string_flagged(self):
        df = pd.DataFrame({
            "customer_id": [1],
            "date_of_birth": ["not-a-date"],
            "registration_date": ["2022-01-15"],
        })
        results = check_dates(df, "customers")
        invalid = [r for r in results
                   if r.check_type == CheckType.INVALID_DATE.value
                   and r.column_name == "date_of_birth"]
        assert any(r.failed_records > 0 for r in invalid)

    def test_null_dates_pass_date_check(self):
        df = pd.DataFrame({
            "customer_id": [1],
            "date_of_birth": [None],
            "registration_date": ["2022-01-15"],
        })
        results = check_dates(df, "customers")
        future = [r for r in results
                  if r.check_type == CheckType.FUTURE_DATE.value
                  and r.column_name == "date_of_birth"]
        assert all(r.failed_records == 0 for r in future)


# -------------------------------------------------------
# Numeric checks
# -------------------------------------------------------

class TestCheckNumerics:

    def test_positive_price_passes(self):
        df = pd.DataFrame({"unit_price": ["99.99"], "cost_price": ["50.00"]})
        results = check_numerics(df, "products")
        failed = [r for r in results if not r.passed]
        assert len(failed) == 0

    def test_negative_price_flagged(self):
        df = pd.DataFrame({"unit_price": ["-10"], "cost_price": ["5"]})
        results = check_numerics(df, "products")
        neg = [r for r in results
               if r.check_type == CheckType.NEGATIVE_VALUE.value
               and r.column_name == "unit_price"]
        assert any(r.failed_records > 0 for r in neg)

    def test_zero_unit_price_flagged(self):
        df = pd.DataFrame({"unit_price": ["0"], "cost_price": ["0"]})
        results = check_numerics(df, "products")
        zero = [r for r in results
                if r.check_type == CheckType.ZERO_VALUE.value
                and r.column_name == "unit_price"]
        assert any(r.failed_records > 0 for r in zero)

    def test_negative_stock_flagged(self):
        df = pd.DataFrame({"stock_quantity": ["-5"]})
        results = check_numerics(df, "inventory")
        assert any(not r.passed for r in results)

    def test_discount_above_100_flagged(self):
        df = pd.DataFrame({
            "discount_pct": ["150"], "tax_pct": ["18"],
            "unit_price": ["100"], "quantity": ["1"],
            "net_amount": ["85"], "tax_amount": ["15.3"],
            "line_total": ["100.3"],
        })
        results = check_numerics(df, "order_items")
        range_fail = [r for r in results
                      if r.column_name == "discount_pct" and not r.passed]
        assert len(range_fail) > 0


# -------------------------------------------------------
# String checks
# -------------------------------------------------------

class TestCheckStrings:

    def test_clean_strings_pass(self):
        df = pd.DataFrame({"first_name": ["Aarav", "Priya"]})
        results = check_strings(df, "customers")
        failed = [r for r in results if not r.passed]
        assert len(failed) == 0

    def test_leading_space_flagged(self):
        df = pd.DataFrame({"first_name": [" Aarav"]})
        results = check_strings(df, "customers")
        ws = [r for r in results
              if r.check_type == CheckType.LEADING_OR_TRAILING_WHITESPACE.value]
        assert any(r.failed_records > 0 for r in ws)

    def test_trailing_space_flagged(self):
        df = pd.DataFrame({"first_name": ["Aarav "]})
        results = check_strings(df, "customers")
        ws = [r for r in results
              if r.check_type == CheckType.LEADING_OR_TRAILING_WHITESPACE.value]
        assert any(r.failed_records > 0 for r in ws)

    def test_multiple_spaces_flagged(self):
        df = pd.DataFrame({"first_name": ["Aarav  Kumar"]})
        results = check_strings(df, "customers")
        ms = [r for r in results
              if r.check_type == CheckType.MULTIPLE_SPACES.value]
        assert any(r.failed_records > 0 for r in ms)

    def test_empty_string_flagged(self):
        df = pd.DataFrame({"first_name": [""]})
        results = check_strings(df, "customers")
        empty = [r for r in results
                 if r.check_type == CheckType.EMPTY_STRING.value]
        assert any(r.failed_records > 0 for r in empty)


# -------------------------------------------------------
# Email validation
# -------------------------------------------------------

class TestCheckEmails:

    def test_valid_email_passes(self):
        df = pd.DataFrame({"email": ["user@example.com"]})
        results = check_emails(df, "customers")
        assert all(r.passed for r in results)

    @pytest.mark.parametrize("bad_email", [
        "notanemail",
        "double@@domain.com",
        "user@",
        "@nodomain.com",
        "no-at-sign",
    ])
    def test_invalid_email_flagged(self, bad_email):
        df = pd.DataFrame({"email": [bad_email]})
        results = check_emails(df, "customers")
        assert any(not r.passed for r in results)

    def test_null_email_not_flagged_by_email_check(self):
        df = pd.DataFrame({"email": [None]})
        results = check_emails(df, "customers")
        assert all(r.passed for r in results)


# -------------------------------------------------------
# Phone validation
# -------------------------------------------------------

class TestCheckPhones:

    def test_valid_10_digit_phone(self):
        df = pd.DataFrame({"phone": ["9876543210"]})
        results = check_phones(df, "customers")
        assert all(r.passed for r in results)

    def test_valid_international_phone(self):
        df = pd.DataFrame({"phone": ["+1 800 555 1234"]})
        results = check_phones(df, "customers")
        assert all(r.passed for r in results)

    def test_too_short_phone_flagged(self):
        df = pd.DataFrame({"phone": ["123"]})
        results = check_phones(df, "customers")
        assert any(not r.passed for r in results)

    def test_letters_in_phone_flagged(self):
        df = pd.DataFrame({"phone": ["ABCDE12345"]})
        results = check_phones(df, "customers")
        assert any(not r.passed for r in results)


# -------------------------------------------------------
# Categorical checks
# -------------------------------------------------------

class TestCheckCategories:

    def test_valid_category_passes(self):
        df = pd.DataFrame({"status": ["Active", "Inactive", "Blocked"]})
        results = check_categories(df, "customers")
        assert all(r.passed for r in results)

    def test_invalid_category_flagged(self):
        df = pd.DataFrame({"status": ["Active", "UNKNOWN"]})
        results = check_categories(df, "customers")
        cat = [r for r in results if r.check_type == CheckType.INVALID_CATEGORY.value]
        assert any(r.failed_records > 0 for r in cat)

    def test_case_insensitive_match(self):
        df = pd.DataFrame({"status": ["active"]})  # lowercase
        results = check_categories(df, "customers")
        cat = [r for r in results if r.check_type == CheckType.INVALID_CATEGORY.value]
        assert all(r.passed for r in cat)


# -------------------------------------------------------
# Business rules
# -------------------------------------------------------

class TestCheckBusinessRules:

    def test_rule001_positive_price_passes(self):
        df = pd.DataFrame({"unit_price": ["99.99"], "cost_price": ["50.00"]})
        results = check_business_rules(df, "products")
        r1 = [r for r in results if r.rule_id == "RULE001"]
        assert all(r.passed for r in r1)

    def test_rule001_zero_price_fails(self):
        df = pd.DataFrame({"unit_price": ["0"], "cost_price": ["0"]})
        results = check_business_rules(df, "products")
        r1 = [r for r in results if r.rule_id == "RULE001"]
        assert any(not r.passed for r in r1)

    def test_rule002_cost_above_price_fails(self):
        df = pd.DataFrame({"unit_price": ["50"], "cost_price": ["100"]})
        results = check_business_rules(df, "products")
        r2 = [r for r in results if r.rule_id == "RULE002"]
        assert any(not r.passed for r in r2)

    def test_rule002_cost_equal_to_price_passes(self):
        df = pd.DataFrame({"unit_price": ["100"], "cost_price": ["100"]})
        results = check_business_rules(df, "products")
        r2 = [r for r in results if r.rule_id == "RULE002"]
        assert all(r.passed for r in r2)

    def test_rule010_delivery_before_shipment_fails(self):
        df = pd.DataFrame({
            "shipment_date": ["2024-06-10"],
            "delivery_date": ["2024-06-05"],  # before shipment
        })
        results = check_business_rules(df, "shipments")
        r10 = [r for r in results if r.rule_id == "RULE010"]
        assert any(not r.passed for r in r10)

    def test_rule010_delivery_after_shipment_passes(self):
        df = pd.DataFrame({
            "shipment_date": ["2024-06-10"],
            "delivery_date": ["2024-06-15"],
        })
        results = check_business_rules(df, "shipments")
        r10 = [r for r in results if r.rule_id == "RULE010"]
        assert all(r.passed for r in r10)

    def test_rule011_inconsistent_line_total_fails(self):
        df = pd.DataFrame({
            "order_item_id": [1], "order_id": [1], "product_id": [1],
            "quantity": ["2"], "unit_price": ["100"],
            "discount_pct": ["0"], "tax_pct": ["18"],
            "net_amount": ["200"], "tax_amount": ["36"],
            "line_total": ["300"],  # should be 236
        })
        results = check_business_rules(df, "order_items")
        r11 = [r for r in results if r.rule_id == "RULE011"]
        assert any(not r.passed for r in r11)


# -------------------------------------------------------
# Results to DataFrame
# -------------------------------------------------------

class TestResultsToDataframe:

    def test_empty_results_returns_dataframe_with_columns(self):
        df = results_to_dataframe([])
        assert "check_id" in df.columns
        assert "severity" in df.columns
        assert len(df) == 0

    def test_results_converted_correctly(self):
        df_input = pd.DataFrame({"customer_id": [1, 2]})
        results = check_primary_key(df_input, "customers")
        df = results_to_dataframe(results)
        assert len(df) == len(results)
        assert "failed_records" in df.columns
