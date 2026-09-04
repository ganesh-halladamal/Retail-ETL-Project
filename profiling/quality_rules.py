"""
===========================================
Profiling - Quality Rules & Metadata
===========================================
Metadata-driven configuration for the profiling
framework. Everything the quality engine needs to
know about the source schema lives here, so adding
a table or rule never requires touching engine code.

Contains:
    Severity / CheckType enums
    QualityResult dataclass (standard result format)
    PRIMARY_KEYS, FOREIGN_KEYS
    REQUIRED_COLUMNS, EXPECTED_DTYPES
    CATEGORICAL_VALUES, DATE_COLUMNS, FUTURE_DATE_COLUMNS
    EMAIL_COLUMNS, PHONE_COLUMNS
    NUMERIC_RULES, BUSINESS_RULES
    SEVERITY_BY_CHECK
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import pandas as pd


class Severity(str, Enum):
    """Severity levels for quality findings, most to least urgent."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


# Ordering used when sorting findings by urgency
SEVERITY_ORDER: Dict[str, int] = {
    Severity.CRITICAL.value: 0,
    Severity.HIGH.value: 1,
    Severity.MEDIUM.value: 2,
    Severity.LOW.value: 3,
    Severity.INFO.value: 4,
}


class CheckType(str, Enum):
    """Categories of quality check performed by the engine."""

    NULL_VALUE = "NULL_VALUE"
    EMPTY_STRING = "EMPTY_STRING"
    WHITESPACE = "WHITESPACE"
    DUPLICATE_ROW = "DUPLICATE_ROW"
    DUPLICATE_PRIMARY_KEY = "DUPLICATE_PRIMARY_KEY"
    NULL_PRIMARY_KEY = "NULL_PRIMARY_KEY"
    INVALID_PRIMARY_KEY = "INVALID_PRIMARY_KEY"
    DATA_TYPE_MISMATCH = "DATA_TYPE_MISMATCH"
    INVALID_DATE = "INVALID_DATE"
    FUTURE_DATE = "FUTURE_DATE"
    DATE_OUT_OF_RANGE = "DATE_OUT_OF_RANGE"
    DATE_SEQUENCE = "DATE_SEQUENCE"
    NEGATIVE_VALUE = "NEGATIVE_VALUE"
    ZERO_VALUE = "ZERO_VALUE"
    LEADING_OR_TRAILING_WHITESPACE = "LEADING_OR_TRAILING_WHITESPACE"
    MULTIPLE_SPACES = "MULTIPLE_SPACES"
    EXCESSIVE_LENGTH = "EXCESSIVE_LENGTH"
    INVALID_EMAIL = "INVALID_EMAIL"
    INVALID_PHONE = "INVALID_PHONE"
    INVALID_CATEGORY = "INVALID_CATEGORY"
    BUSINESS_RULE = "BUSINESS_RULE"
    POTENTIAL_OUTLIER = "POTENTIAL_OUTLIER"
    FOREIGN_KEY = "FOREIGN_KEY"


class DataTypeCategory(str, Enum):
    """Logical data type categories used for mismatch detection."""

    INTEGER = "INTEGER"
    DECIMAL = "DECIMAL"
    STRING = "STRING"
    DATE = "DATE"
    DATETIME = "DATETIME"
    BOOLEAN = "BOOLEAN"
    UNKNOWN = "UNKNOWN"


# Maximum sample failing values recorded per finding
SAMPLE_LIMIT: int = 5


@dataclass
class QualityResult:
    """
    Standardised result for a single quality check.

    One instance is produced per check that runs, whether or
    not it found failures, so pass rates can be reported.
    """

    check_id: str
    rule_id: str
    table_name: str
    column_name: str
    check_type: str
    description: str
    total_records: int
    passed_records: int
    failed_records: int
    failure_percentage: float
    severity: str
    sample_values: str = ""
    execution_timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    @property
    def passed(self) -> bool:
        """True when the check found no failing records."""
        return self.failed_records == 0

    def to_dict(self) -> Dict[str, Any]:
        """Return a flat dictionary suitable for DataFrame construction."""
        return {
            "check_id": self.check_id,
            "rule_id": self.rule_id,
            "table_name": self.table_name,
            "column_name": self.column_name,
            "check_type": self.check_type,
            "description": self.description,
            "total_records": self.total_records,
            "passed_records": self.passed_records,
            "failed_records": self.failed_records,
            "failure_percentage": self.failure_percentage,
            "severity": self.severity,
            "sample_values": self.sample_values,
            "execution_timestamp": self.execution_timestamp,
        }


# ===========================================
# PRIMARY KEYS
# ===========================================
PRIMARY_KEYS: Dict[str, str] = {
    "customers": "customer_id",
    "categories": "category_id",
    "products": "product_id",
    "suppliers": "supplier_id",
    "stores": "store_id",
    "employees": "employee_id",
    "inventory": "inventory_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "payments": "payment_id",
    "shipments": "shipment_id",
    "returns": "return_id",
}


@dataclass(frozen=True)
class ForeignKey:
    """A child -> parent relationship to validate."""

    child_table: str
    child_column: str
    parent_table: str
    parent_column: str
    severity: str = Severity.HIGH.value

    @property
    def label(self) -> str:
        """Human readable relationship label."""
        return (
            f"{self.child_table}.{self.child_column} -> "
            f"{self.parent_table}.{self.parent_column}"
        )


# ===========================================
# FOREIGN KEYS
# ===========================================
FOREIGN_KEYS: List[ForeignKey] = [
    ForeignKey("products", "category_id", "categories", "category_id"),
    ForeignKey("products", "supplier_id", "suppliers", "supplier_id"),
    ForeignKey("employees", "store_id", "stores", "store_id"),
    ForeignKey("inventory", "product_id", "products", "product_id"),
    ForeignKey("inventory", "store_id", "stores", "store_id"),
    ForeignKey("orders", "customer_id", "customers", "customer_id"),
    ForeignKey("orders", "store_id", "stores", "store_id"),
    ForeignKey("orders", "employee_id", "employees", "employee_id"),
    ForeignKey("order_items", "order_id", "orders", "order_id"),
    ForeignKey("order_items", "product_id", "products", "product_id"),
    ForeignKey("payments", "order_id", "orders", "order_id"),
    ForeignKey("shipments", "order_id", "orders", "order_id"),
    ForeignKey("returns", "order_item_id", "order_items", "order_item_id"),
]


# ===========================================
# EXPECTED DATA TYPES
# ===========================================
_INT = DataTypeCategory.INTEGER.value
_DEC = DataTypeCategory.DECIMAL.value
_STR = DataTypeCategory.STRING.value
_DATE = DataTypeCategory.DATE.value
_DTTM = DataTypeCategory.DATETIME.value

EXPECTED_DTYPES: Dict[str, Dict[str, str]] = {
    "customers": {
        "customer_id": _INT, "first_name": _STR, "last_name": _STR,
        "gender": _STR, "email": _STR, "phone": _STR,
        "date_of_birth": _DATE, "city": _STR, "state": _STR,
        "country": _STR, "registration_date": _DATE, "status": _STR,
    },
    "categories": {
        "category_id": _INT, "category_name": _STR, "description": _STR,
    },
    "suppliers": {
        "supplier_id": _INT, "supplier_name": _STR, "contact_person": _STR,
        "email": _STR, "phone": _STR, "city": _STR, "country": _STR,
    },
    "products": {
        "product_id": _INT, "category_id": _INT, "supplier_id": _INT,
        "product_name": _STR, "brand": _STR, "unit_price": _DEC,
        "cost_price": _DEC, "created_date": _DATE, "status": _STR,
    },
    "stores": {
        "store_id": _INT, "store_name": _STR, "city": _STR,
        "state": _STR, "manager_name": _STR, "opened_date": _DATE,
    },
    "employees": {
        "employee_id": _INT, "store_id": _INT, "first_name": _STR,
        "last_name": _STR, "designation": _STR, "salary": _DEC,
        "hire_date": _DATE,
    },
    "inventory": {
        "inventory_id": _INT, "product_id": _INT, "store_id": _INT,
        "stock_quantity": _INT, "last_updated": _DTTM,
    },
    "orders": {
        "order_id": _INT, "customer_id": _INT, "store_id": _INT,
        "employee_id": _INT, "order_date": _DTTM,
        "order_status": _STR, "total_amount": _DEC,
    },
    "order_items": {
        "order_item_id": _INT, "order_id": _INT, "product_id": _INT,
        "quantity": _INT, "unit_price": _DEC, "discount_pct": _DEC,
        "tax_pct": _DEC, "net_amount": _DEC, "tax_amount": _DEC,
        "line_total": _DEC,
    },
    "payments": {
        "payment_id": _INT, "order_id": _INT, "payment_method": _STR,
        "payment_status": _STR, "payment_date": _DTTM, "amount_paid": _DEC,
    },
    "shipments": {
        "shipment_id": _INT, "order_id": _INT, "shipping_partner": _STR,
        "tracking_number": _STR, "shipment_date": _DATE,
        "delivery_date": _DATE, "shipment_status": _STR,
    },
    "returns": {
        "return_id": _INT, "order_item_id": _INT, "return_reason": _STR,
        "return_date": _DATE, "refund_amount": _DEC,
    },
}


# ===========================================
# REQUIRED (NOT NULL) COLUMNS
# Nulls here are HIGH severity; other columns are LOW.
# ===========================================
REQUIRED_COLUMNS: Dict[str, List[str]] = {
    "customers": [
        "first_name", "last_name", "gender", "email", "phone",
        "date_of_birth", "city", "state", "country",
        "registration_date", "status",
    ],
    "categories": ["category_name"],
    "suppliers": [
        "supplier_name", "contact_person", "email", "phone", "city", "country",
    ],
    "products": [
        "category_id", "supplier_id", "product_name", "brand",
        "unit_price", "cost_price", "created_date", "status",
    ],
    "stores": ["store_name", "city", "state", "manager_name", "opened_date"],
    "employees": [
        "store_id", "first_name", "last_name", "designation",
        "salary", "hire_date",
    ],
    "inventory": ["product_id", "store_id", "stock_quantity", "last_updated"],
    "orders": [
        "customer_id", "store_id", "employee_id", "order_date",
        "order_status", "total_amount",
    ],
    "order_items": [
        "order_id", "product_id", "quantity", "unit_price",
        "discount_pct", "tax_pct", "net_amount", "tax_amount", "line_total",
    ],
    "payments": [
        "order_id", "payment_method", "payment_status",
        "payment_date", "amount_paid",
    ],
    "shipments": [
        "order_id", "shipping_partner", "tracking_number",
        "shipment_date", "shipment_status",
    ],
    "returns": ["order_item_id", "return_reason", "return_date", "refund_amount"],
}

# Columns allowed to be null by design (excluded from null findings)
NULLABLE_BY_DESIGN: Dict[str, List[str]] = {
    "categories": ["description"],
    "shipments": ["delivery_date"],
}


# ===========================================
# CATEGORICAL DOMAINS
# Values outside these sets are flagged INVALID_CATEGORY.
# Comparison is case-insensitive and whitespace-trimmed.
# ===========================================
CATEGORICAL_VALUES: Dict[str, Dict[str, List[str]]] = {
    "customers": {
        "gender": ["Male", "Female", "Other"],
        "status": ["Active", "Inactive", "Blocked"],
    },
    "products": {
        "status": ["Active", "Discontinued", "Out of Stock"],
    },
    "orders": {
        "order_status": [
            "Pending", "Processing", "Shipped",
            "Delivered", "Cancelled", "Returned",
        ],
    },
    "payments": {
        "payment_method": [
            "Credit Card", "Debit Card", "UPI",
            "Net Banking", "Cash", "Wallet",
        ],
        "payment_status": ["Pending", "Completed", "Failed", "Refunded"],
    },
    "shipments": {
        "shipment_status": [
            "Dispatched", "In Transit", "Out for Delivery",
            "Delivered", "Failed",
        ],
    },
}

# ===========================================
# DATE / DATETIME COLUMNS
# ===========================================
DATE_COLUMNS: Dict[str, List[str]] = {
    "customers": ["date_of_birth", "registration_date"],
    "products": ["created_date"],
    "stores": ["opened_date"],
    "employees": ["hire_date"],
    "inventory": ["last_updated"],
    "orders": ["order_date"],
    "payments": ["payment_date"],
    "shipments": ["shipment_date", "delivery_date"],
    "returns": ["return_date"],
}

# Columns that must never hold a future date
FUTURE_DATE_COLUMNS: Dict[str, List[str]] = {
    "customers": ["date_of_birth", "registration_date"],
    "products": ["created_date"],
    "stores": ["opened_date"],
    "employees": ["hire_date"],
    "orders": ["order_date"],
    "payments": ["payment_date"],
    "shipments": ["shipment_date"],
    "returns": ["return_date"],
}

# Earliest plausible business date; anything before this is suspect
MIN_REASONABLE_DATE: str = "1900-01-01"
# Birth dates before this are implausible for a live customer
MIN_REASONABLE_BIRTH_DATE: str = "1920-01-01"


# ===========================================
# EMAIL / PHONE COLUMNS
# ===========================================
EMAIL_COLUMNS: Dict[str, List[str]] = {
    "customers": ["email"],
    "suppliers": ["email"],
}

PHONE_COLUMNS: Dict[str, List[str]] = {
    "customers": ["phone"],
    "suppliers": ["phone"],
}

# Pragmatic email pattern: one @, no consecutive dots, TLD of 2+ chars
EMAIL_PATTERN: str = (
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9]([A-Za-z0-9\-]*[A-Za-z0-9])?"
    r"(\.[A-Za-z0-9]([A-Za-z0-9\-]*[A-Za-z0-9])?)*\.[A-Za-z]{2,}$"
)

# Phone validation is deliberately country-agnostic and configurable:
# digits are counted after stripping common separators and an optional
# international prefix.
PHONE_ALLOWED_PATTERN: str = r"^\+?[0-9\s\-().]+$"
PHONE_MIN_DIGITS: int = 7
PHONE_MAX_DIGITS: int = 15

# ===========================================
# STRING QUALITY THRESHOLDS
# ===========================================
# Values longer than this are flagged EXCESSIVE_LENGTH
MAX_STRING_LENGTH: Dict[str, int] = {
    "default": 255,
    "description": 500,
    "return_reason": 500,
}

# Tokens treated as null-equivalent when read from CSV
NULL_LIKE_TOKENS: List[str] = ["", "NULL", "null", "None", "NaN", "nan", "N/A", "na"]


@dataclass(frozen=True)
class NumericRule:
    """Constraints for a single numeric column."""

    table: str
    column: str
    allow_negative: bool = False
    allow_zero: bool = True
    min_value: Optional[float] = None
    max_value: Optional[float] = None


# ===========================================
# NUMERIC COLUMN RULES
# ===========================================
NUMERIC_RULES: List[NumericRule] = [
    NumericRule("products", "unit_price", allow_negative=False, allow_zero=False),
    NumericRule("products", "cost_price", allow_negative=False, allow_zero=False),
    NumericRule("employees", "salary", allow_negative=False, allow_zero=False),
    NumericRule("inventory", "stock_quantity", allow_negative=False, allow_zero=True),
    NumericRule("orders", "total_amount", allow_negative=False, allow_zero=True),
    NumericRule("order_items", "quantity", allow_negative=False, allow_zero=False),
    NumericRule("order_items", "unit_price", allow_negative=False, allow_zero=False),
    NumericRule(
        "order_items", "discount_pct",
        allow_negative=False, allow_zero=True, min_value=0, max_value=100,
    ),
    NumericRule(
        "order_items", "tax_pct",
        allow_negative=False, allow_zero=True, min_value=0, max_value=100,
    ),
    NumericRule("order_items", "net_amount", allow_negative=False, allow_zero=True),
    NumericRule("order_items", "tax_amount", allow_negative=False, allow_zero=True),
    NumericRule("order_items", "line_total", allow_negative=False, allow_zero=True),
    NumericRule("payments", "amount_paid", allow_negative=False, allow_zero=True),
    NumericRule("returns", "refund_amount", allow_negative=False, allow_zero=True),
]

# Numeric columns to scan for IQR outliers
OUTLIER_COLUMNS: Dict[str, List[str]] = {
    "products": ["unit_price", "cost_price"],
    "employees": ["salary"],
    "inventory": ["stock_quantity"],
    "orders": ["total_amount"],
    "order_items": ["quantity", "unit_price", "line_total"],
    "payments": ["amount_paid"],
    "returns": ["refund_amount"],
}

IQR_MULTIPLIER: float = 1.5


@dataclass(frozen=True)
class BusinessRule:
    """
    A declarative business rule.

    The predicate receives the table DataFrame and returns a boolean
    Series that is True for PASSING rows. Rows where the predicate is
    False are counted as failures; null inputs are treated as passing
    here because nulls are reported separately by the null checks.
    """

    rule_id: str
    table: str
    columns: List[str]
    description: str
    predicate: Callable[[pd.DataFrame], pd.Series]
    severity: str = Severity.HIGH.value
    business_reason: str = ""

    @property
    def column_label(self) -> str:
        """Comma separated column list for reporting."""
        return ", ".join(self.columns)


def _numeric(df: pd.DataFrame, column: str) -> pd.Series:
    """Coerce a column to numeric, returning NaN for unparseable values."""
    return pd.to_numeric(df[column], errors="coerce")


def _dates(df: pd.DataFrame, column: str) -> pd.Series:
    """Coerce a column to datetime, returning NaT for unparseable values."""
    return pd.to_datetime(df[column], errors="coerce")


def _gt_zero(column: str) -> Callable[[pd.DataFrame], pd.Series]:
    """Build a predicate asserting column > 0 (nulls pass)."""

    def predicate(df: pd.DataFrame) -> pd.Series:
        values = _numeric(df, column)
        return values.isna() | (values > 0)

    return predicate


def _gte_zero(column: str) -> Callable[[pd.DataFrame], pd.Series]:
    """Build a predicate asserting column >= 0 (nulls pass)."""

    def predicate(df: pd.DataFrame) -> pd.Series:
        values = _numeric(df, column)
        return values.isna() | (values >= 0)

    return predicate


def _not_future(column: str) -> Callable[[pd.DataFrame], pd.Series]:
    """Build a predicate asserting a date is not in the future (nulls pass)."""

    def predicate(df: pd.DataFrame) -> pd.Series:
        values = _dates(df, column)
        return values.isna() | (values <= pd.Timestamp.now())

    return predicate


def _cost_not_above_price(df: pd.DataFrame) -> pd.Series:
    """RULE002 predicate: cost_price must not exceed unit_price."""
    cost = _numeric(df, "cost_price")
    price = _numeric(df, "unit_price")
    return cost.isna() | price.isna() | (cost <= price)


def _delivery_not_before_shipment(df: pd.DataFrame) -> pd.Series:
    """RULE010 predicate: delivery_date must not precede shipment_date."""
    shipped = _dates(df, "shipment_date")
    delivered = _dates(df, "delivery_date")
    return shipped.isna() | delivered.isna() | (delivered >= shipped)


def _line_total_consistent(df: pd.DataFrame) -> pd.Series:
    """RULE011 predicate: line_total must equal net_amount + tax_amount."""
    net = _numeric(df, "net_amount")
    tax = _numeric(df, "tax_amount")
    total = _numeric(df, "line_total")
    missing = net.isna() | tax.isna() | total.isna()
    # Allow one paisa of rounding tolerance
    return missing | ((net + tax - total).abs() <= 0.01)


# ===========================================
# BUSINESS RULES
# ===========================================
BUSINESS_RULES: List[BusinessRule] = [
    BusinessRule(
        "RULE001", "products", ["unit_price"],
        "Product unit_price must be greater than zero.",
        _gt_zero("unit_price"), Severity.HIGH.value,
        "A zero or negative selling price corrupts all revenue reporting.",
    ),
    BusinessRule(
        "RULE002", "products", ["cost_price", "unit_price"],
        "Product cost_price must be less than or equal to unit_price.",
        _cost_not_above_price, Severity.MEDIUM.value,
        "Cost above price implies a loss-making product and skews margin analysis.",
    ),
    BusinessRule(
        "RULE003", "inventory", ["stock_quantity"],
        "Inventory stock_quantity cannot be negative.",
        _gte_zero("stock_quantity"), Severity.HIGH.value,
        "Negative stock is physically impossible and breaks availability logic.",
    ),
    BusinessRule(
        "RULE004", "orders", ["total_amount"],
        "Order total_amount cannot be negative.",
        _gte_zero("total_amount"), Severity.HIGH.value,
        "Negative order totals understate revenue in the sales fact table.",
    ),
    BusinessRule(
        "RULE005", "order_items", ["quantity"],
        "Order item quantity must be greater than zero.",
        _gt_zero("quantity"), Severity.HIGH.value,
        "A line with no quantity should not exist as a sale.",
    ),
]

BUSINESS_RULES.extend([
    BusinessRule(
        "RULE006", "payments", ["amount_paid"],
        "Payment amount_paid cannot be negative.",
        _gte_zero("amount_paid"), Severity.HIGH.value,
        "Negative payments distort cash reconciliation.",
    ),
    BusinessRule(
        "RULE007", "returns", ["refund_amount"],
        "Refund amount cannot be negative.",
        _gte_zero("refund_amount"), Severity.HIGH.value,
        "Negative refunds invert the sign of returns reporting.",
    ),
    BusinessRule(
        "RULE008", "customers", ["date_of_birth"],
        "Customer date_of_birth cannot be a future date.",
        _not_future("date_of_birth"), Severity.MEDIUM.value,
        "A future birth date makes age segmentation meaningless.",
    ),
    BusinessRule(
        "RULE009", "employees", ["hire_date"],
        "Employee hire_date cannot be a future date.",
        _not_future("hire_date"), Severity.MEDIUM.value,
        "Future hire dates break tenure and headcount reporting.",
    ),
    BusinessRule(
        "RULE010", "shipments", ["shipment_date", "delivery_date"],
        "Delivery date cannot be before shipment date.",
        _delivery_not_before_shipment, Severity.HIGH.value,
        "Delivery preceding dispatch is impossible and breaks lead-time metrics.",
    ),
    BusinessRule(
        "RULE011", "order_items", ["net_amount", "tax_amount", "line_total"],
        "Order item line_total must equal net_amount plus tax_amount.",
        _line_total_consistent, Severity.HIGH.value,
        "Inconsistent totals mean net revenue and tax cannot be trusted.",
    ),
])

# ===========================================
# CROSS-TABLE DATE RULES
# Validated after all tables are loaded, via a join
# on the child's foreign key.
# ===========================================
@dataclass(frozen=True)
class CrossTableDateRule:
    """A date ordering rule spanning two related tables."""

    rule_id: str
    child_table: str
    child_date_column: str
    child_key: str
    parent_table: str
    parent_key: str
    parent_date_column: str
    description: str
    severity: str = Severity.HIGH.value
    business_reason: str = ""


CROSS_TABLE_DATE_RULES: List[CrossTableDateRule] = [
    CrossTableDateRule(
        "RULE012", "shipments", "shipment_date", "order_id",
        "orders", "order_id", "order_date",
        "Shipment date must not be before the related order date.",
        Severity.HIGH.value,
        "Dispatch before the order exists indicates a data or process fault.",
    ),
    CrossTableDateRule(
        "RULE013", "payments", "payment_date", "order_id",
        "orders", "order_id", "order_date",
        "Payment date must not be before the related order date.",
        Severity.MEDIUM.value,
        "Payment before order creation breaks the order-to-cash timeline.",
    ),
]


# ===========================================
# SEVERITY CONFIGURATION
# Every check type maps to a configurable severity.
# ===========================================
SEVERITY_BY_CHECK: Dict[str, str] = {
    CheckType.NULL_PRIMARY_KEY.value: Severity.CRITICAL.value,
    CheckType.DUPLICATE_PRIMARY_KEY.value: Severity.CRITICAL.value,
    CheckType.INVALID_PRIMARY_KEY.value: Severity.CRITICAL.value,
    CheckType.FOREIGN_KEY.value: Severity.HIGH.value,
    CheckType.DUPLICATE_ROW.value: Severity.HIGH.value,
    CheckType.NULL_VALUE.value: Severity.HIGH.value,
    CheckType.DATA_TYPE_MISMATCH.value: Severity.HIGH.value,
    CheckType.NEGATIVE_VALUE.value: Severity.HIGH.value,
    CheckType.DATE_SEQUENCE.value: Severity.HIGH.value,
    CheckType.INVALID_DATE.value: Severity.HIGH.value,
    CheckType.BUSINESS_RULE.value: Severity.HIGH.value,
    CheckType.FUTURE_DATE.value: Severity.MEDIUM.value,
    CheckType.DATE_OUT_OF_RANGE.value: Severity.MEDIUM.value,
    CheckType.INVALID_EMAIL.value: Severity.MEDIUM.value,
    CheckType.INVALID_PHONE.value: Severity.MEDIUM.value,
    CheckType.INVALID_CATEGORY.value: Severity.MEDIUM.value,
    CheckType.ZERO_VALUE.value: Severity.MEDIUM.value,
    CheckType.EMPTY_STRING.value: Severity.MEDIUM.value,
    CheckType.EXCESSIVE_LENGTH.value: Severity.LOW.value,
    CheckType.LEADING_OR_TRAILING_WHITESPACE.value: Severity.LOW.value,
    CheckType.MULTIPLE_SPACES.value: Severity.LOW.value,
    CheckType.WHITESPACE.value: Severity.LOW.value,
    CheckType.POTENTIAL_OUTLIER.value: Severity.INFO.value,
}

# Null severity depends on the column's role
NULL_SEVERITY_PRIMARY_KEY: str = Severity.CRITICAL.value
NULL_SEVERITY_REQUIRED: str = Severity.HIGH.value
NULL_SEVERITY_OPTIONAL: str = Severity.LOW.value


def severity_for(check_type: str) -> str:
    """
    Look up the configured severity for a check type.

    Args:
        check_type: Value from CheckType

    Returns:
        str: Severity value, defaulting to MEDIUM when unmapped
    """
    return SEVERITY_BY_CHECK.get(check_type, Severity.MEDIUM.value)


# ===========================================
# QUALITY SCORE WEIGHTS
# Documented in docs/data_quality_rules.md
# ===========================================
SCORE_WEIGHTS: Dict[str, float] = {
    "completeness": 0.25,
    "uniqueness": 0.20,
    "validity": 0.25,
    "consistency": 0.15,
    "referential_integrity": 0.15,
}

# Expected tables, used to confirm discovery found everything
EXPECTED_TABLES: List[str] = list(PRIMARY_KEYS.keys())
