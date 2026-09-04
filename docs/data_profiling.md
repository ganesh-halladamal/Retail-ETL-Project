# Data Profiling

## What is Data Profiling?

Data profiling is the process of examining raw source data to understand its structure, content, and quality **before** any transformation or loading takes place. It answers questions like:

- How complete is this data?
- Are there duplicates?
- Do values match their expected types and formats?
- Do foreign key relationships hold?
- Are there business rule violations?

## Why Profile Before Transforming?

Profiling first means transformation code can be written with full knowledge of the actual data, not assumptions about it. Discovered issues are documented as recommended actions rather than silently ignored. The ETL pipeline maintains a strict separation:

```
RAW DATA
   ↓
PROFILING & QUALITY ASSESSMENT   ← Phase 5 (this phase)
   ↓
CLEANING / TRANSFORMATION        ← Phase 6
   ↓
WAREHOUSE LOAD                   ← Phase 7
```

Raw data is **never modified** by profiling.

## Framework Architecture

```
profiling/
├── quality_rules.py          Metadata configuration (PKs, FKs, rules, domains)
├── column_profiler.py        Per-column statistics and type detection
├── table_profiler.py         Per-table metrics (row counts, duplicates, nulls)
├── quality_engine.py         All quality checks (null, duplicate, date, numeric…)
├── referential_integrity.py  Foreign key validation across tables
├── anomaly_detector.py       IQR outlier detection
├── profiler.py               Orchestrator, scoring, and ProfilingRun dataclass
├── report_generator.py       CSV, JSON, and HTML report writing
└── profile_runner.py         CLI entry point
```

## Execution Flow

```
profile_runner.py
  │
  ├─ discover_csv_files()       find *.csv under data/raw/
  ├─ load_tables()              read-only with dtype=str
  │
  ├─ for each table:
  │    ├─ profile_table()       row/col counts, duplicates, file size
  │    ├─ profile_columns()     per-column statistics
  │    ├─ run_table_checks()    null, PK, type, date, numeric, string,
  │    │                        email, phone, category, business rules
  │    └─ detect_outliers()     IQR scan on configured numeric columns
  │
  ├─ validate_all_relationships()  FK validation across all tables
  ├─ check_cross_table_dates()     multi-table date sequence rules
  ├─ calculate_quality_scores()    5-dimension weighted score per table
  │
  └─ generate_all_reports()
       ├─ data/profiling/table_profiles/
       ├─ data/profiling/column_profiles/
       ├─ data/profiling/quality_results/
       ├─ data/profiling/relationship_results/
       ├─ data/profiling/reports/data_quality_report.html
       └─ docs/data_quality_findings.md
```

## Running the Profiler

```bash
# Profile all tables
python -m profiling.profile_runner

# Profile a single table
python -m profiling.profile_runner --table customers

# Verbose console output
python -m profiling.profile_runner --verbose

# Custom input/output directories
python -m profiling.profile_runner \
    --input-dir data/raw \
    --output-dir data/profiling
```

The runner requires extraction to have been run first (`python main.py`).

## Output Files

| Location | Contents |
|----------|----------|
| `data/profiling/table_profiles/` | Per-table CSV + JSON profile |
| `data/profiling/column_profiles/` | Per-table column statistics CSV + JSON |
| `data/profiling/quality_results/` | All checks, failures, per-severity splits |
| `data/profiling/relationship_results/` | FK integrity CSV + JSON |
| `data/profiling/reports/data_quality_report.csv` | Consolidated findings |
| `data/profiling/reports/data_quality_report.json` | Machine-readable report |
| `data/profiling/reports/data_quality_report.html` | Human-readable HTML report |
| `data/profiling/reports/quality_scores.csv` | Per-table quality scores |
| `logs/profiling.log` | Structured profiling log |
| `docs/data_quality_findings.md` | Auto-generated findings and recommended actions |

## Quality Score Formula

Each table receives a weighted overall quality score:

| Dimension | Weight | Checks Included |
|-----------|--------|-----------------|
| Completeness | 25% | Null checks on required/PK columns |
| Uniqueness | 20% | Duplicate rows, duplicate PKs |
| Validity | 25% | Type mismatches, invalid dates, negative values, bad emails/phones/categories |
| Consistency | 15% | Business rules, date sequences, whitespace |
| Referential Integrity | 15% | Foreign key checks |

`overall_score = Σ(dimension_score × dimension_weight)`

Scores range from 0–100. Outliers are excluded from scoring (flagged INFO, not failures).

## Error Handling

| Situation | Behaviour |
|-----------|-----------|
| Input directory missing | Runner exits code 2 with instructions |
| One CSV fails to load | Logged ERROR, other tables continue |
| One quality check errors | Logged ERROR, other checks continue |
| No critical issues | Exit code 0 |
| Critical issues found | Exit code 1 (safe for CI pipelines) |
