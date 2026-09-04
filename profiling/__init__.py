"""
===========================================
Profiling Module — Phase 5
===========================================
Data Profiling and Quality Assessment layer
for the Retail ETL Pipeline.

This module reads raw CSV extracts from data/raw/,
profiles every table and column, and generates
comprehensive quality reports under data/profiling/.

RAW DATA IS NEVER MODIFIED BY THIS MODULE.

Entry point:
    python -m profiling.profile_runner
    python -m profiling.profile_runner --table customers
    python -m profiling.profile_runner --verbose

Key sub-modules:
    quality_rules        Metadata, rule config, enums, QualityResult
    column_profiler      Per-column statistics
    table_profiler       Per-table statistics
    quality_engine       All quality checks
    referential_integrity Foreign key validation
    anomaly_detector     IQR outlier detection
    profiler             Orchestrator + quality scoring
    report_generator     CSV / JSON / HTML report writing
    profile_runner       CLI entry point
"""
