# Extraction Layer

Reads every transactional table from the `retail_oltp` source database into Pandas DataFrames and writes raw CSV snapshots to `data/raw/`.

This layer performs **extraction only** — no transformation, no warehouse writes.

## Folder Structure

```
extract/
├── __init__.py              # Package exports
├── db_connection.py         # Pooled SQLAlchemy engine + connection test
├── base_extractor.py        # Shared extract_table() + validate_dataframe()
├── extract_categories.py    # One thin module per source table
├── extract_suppliers.py
├── extract_stores.py
├── extract_products.py
├── extract_employees.py
├── extract_customers.py
├── extract_inventory.py
├── extract_orders.py
├── extract_order_items.py
├── extract_payments.py
├── extract_shipments.py
├── extract_returns.py
└── extractor.py             # Master orchestrator
```

## How Extraction Works

Each `extract_<table>.py` module is deliberately thin. It declares the table name and its expected columns, then delegates to the shared `extract_table()` helper in `base_extractor.py`. That helper owns the logic every table needs: acquire a pooled connection, run `SELECT * FROM <table>`, time the query, log the outcome, and return a DataFrame.

This keeps the extraction rules in one place. A change to logging, timing, or error handling is made once and applies to all twelve tables.

`extractor.py` holds the registry that maps each table name to its extract function and expected columns:

```python
TABLE_REGISTRY = {
    "categories": (extract_categories.extract_categories, EXPECTED_COLUMNS),
    ...
}
```

## Execution Flow

```
main.py
  │
  ├─ get_db_config()              read .env via config.py
  ├─ print_banner()               show host, source DB, log path
  │
  └─ extract_all()
       │
       ├─ test_connection()       abort early if DB unreachable
       │
       ├─ for each table in TABLE_REGISTRY:
       │    ├─ extract_table()        SELECT * → DataFrame
       │    ├─ validate_dataframe()   not None, rows > 0, columns present
       │    └─ save_to_csv()          data/raw/<table>.csv (UTF-8)
       │
       ├─ _log_job_summary()      totals, failures, empty tables
       └─ return {table: DataFrame}
  │
  ├─ get_extraction_summary()     tabular per-table report
  └─ close()                      dispose connection pool
```

## Connection Handling

`db_connection.py` builds one pooled engine per process and reuses it for every table:

| Setting | Value | Purpose |
|---|---|---|
| `pool_size` | 5 | Base connections kept open |
| `max_overflow` | 10 | Extra connections under load |
| `pool_timeout` | 30s | Wait limit for a free connection |
| `pool_recycle` | 3600s | Recycle hourly to avoid stale connections |
| `pool_pre_ping` | True | Validate a connection before handing it out |

Credentials come from `.env` through `config.get_connection_string()`, which uses `sqlalchemy.engine.URL.create()` so passwords containing `@`, `:`, `/` or `#` are encoded correctly and stay out of error strings. Nothing is hardcoded.

Call `close()` when finished to dispose the pool.

## Error Handling

The pipeline never stops on a single table failure.

| Situation | Behaviour |
|---|---|
| Database unreachable | Logged as ERROR, job aborts before any table runs, empty dict returned |
| One table fails | Logged as ERROR, table skipped, remaining tables still extracted |
| Table returns 0 rows | Logged as WARNING, DataFrame kept, CSV still written, flagged `EMPTY` in summary |
| Missing expected column | Logged as ERROR, table excluded from the result |
| CSV write fails | Logged as ERROR, DataFrame still returned in memory |

The process exit code is `0` only when all twelve tables succeed, and `1` on partial or total failure — suitable for a scheduler or CI step.

## Logging

All events are written to `logs/extract.log`. Warnings and errors also appear on the console.

Each run records job start, per-table start and finish, row counts, durations, validation outcomes, and a closing summary:

```
2026-08-24 15:47:24 | INFO  | extract.extractor      | EXTRACTION JOB STARTED | tables=12
2026-08-24 15:47:24 | INFO  | extract.base_extractor | [customers] Extraction started.
2026-08-24 15:47:24 | INFO  | extract.base_extractor | [customers] Extraction SUCCESS | rows=100 | columns=12 | duration=0.031s
2026-08-24 15:47:24 | INFO  | extract.extractor      | [customers] Saved 100 rows to data/raw/customers.csv
2026-08-24 15:47:24 | INFO  | extract.extractor      | EXTRACTION JOB SUCCESS | extracted=12 | failed=0 | empty=0 | total_rows=3253 | duration=1.284s
```

## Raw Data Output

Every table is written to `data/raw/<table>.csv` in UTF-8 with no index column. These files are gitignored (they contain customer email, phone and date of birth) while `.gitkeep` is preserved.

## Running It

```bash
python main.py
```

Or use the layer directly:

```python
from extract.extractor import extract_all, close

data = extract_all()          # dict of DataFrames
customers = data["customers"]
close()
```

To skip CSV output and work in memory only:

```python
data = extract_all(save_csv=False)
```

## Adding a New Table

1. Create `extract/extract_<table>.py` following the existing pattern:

```python
"""Extract - <Table>"""

import pandas as pd

from extract.base_extractor import extract_table

TABLE_NAME: str = "<table>"

EXPECTED_COLUMNS: list[str] = ["col_a", "col_b"]


def extract_<table>() -> pd.DataFrame:
    """Extract all <table> records."""
    return extract_table(TABLE_NAME)
```

2. Add the module to the imports and `__all__` list in `extract/__init__.py`.

3. Register it in `TABLE_REGISTRY` in `extract/extractor.py`, placing parent tables before children:

```python
"<table>": (
    extract_<table>.extract_<table>,
    extract_<table>.EXPECTED_COLUMNS,
),
```

4. Update `total_tables` in `main.py` so the summary count stays accurate.

No changes to `base_extractor.py` or `db_connection.py` are needed — logging, timing, pooling, validation and CSV writing are inherited automatically.
