"""
===========================================
Profiling - Report Generator
===========================================
Writes every profiling artefact to disk:

    table_profiles/       per-table CSV + JSON
    column_profiles/      per-table column CSV + JSON
    quality_results/      quality findings CSV + JSON
    relationship_results/ referential integrity CSV
    reports/              consolidated CSV, JSON and HTML

Also refreshes docs/data_quality_findings.md.

All writes go to the output directory only; the raw
input directory is never touched.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from profiling.profiler import PROJECT_ROOT, ProfilingRun
from profiling.quality_rules import Severity
from utils.logger import get_profiling_logger

logger = get_profiling_logger(__name__)

CSV_ENCODING: str = "utf-8"

SUBDIRECTORIES: List[str] = [
    "table_profiles",
    "column_profiles",
    "quality_results",
    "relationship_results",
    "reports",
]


def ensure_output_dirs(output_dir: Path) -> Dict[str, Path]:
    """
    Create the profiling output directory tree.

    Args:
        output_dir: Root output directory (data/profiling)

    Returns:
        Dict[str, Path]: Mapping of subdirectory name to path
    """
    paths: Dict[str, Path] = {}
    for name in SUBDIRECTORIES:
        path = output_dir / name
        path.mkdir(parents=True, exist_ok=True)
        paths[name] = path
    return paths


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    """Write a DataFrame to CSV, logging failures rather than raising."""
    try:
        df.to_csv(path, index=False, encoding=CSV_ENCODING)
    except OSError as exc:
        logger.error("Failed to write %s: %s", path, exc)


def _write_json(payload: Any, path: Path) -> None:
    """Write a JSON payload, logging failures rather than raising."""
    try:
        with path.open("w", encoding=CSV_ENCODING) as handle:
            json.dump(payload, handle, indent=2, default=str)
    except OSError as exc:
        logger.error("Failed to write %s: %s", path, exc)


def write_table_profiles(run: ProfilingRun, output: Dict[str, Path]) -> None:
    """
    Write per-table profiles as CSV and JSON, plus a combined CSV.

    Args:
        run: Completed profiling run
        output: Output directory mapping
    """
    if run.table_profiles.empty:
        return

    directory = output["table_profiles"]
    for row in run.table_profiles.to_dict(orient="records"):
        table = row["table_name"]
        _write_csv(pd.DataFrame([row]), directory / f"{table}_profile.csv")
        _write_json(row, directory / f"{table}_profile.json")

    _write_csv(run.table_profiles, directory / "all_tables_profile.csv")
    logger.info("Table profiles written to %s", directory)


def write_column_profiles(run: ProfilingRun, output: Dict[str, Path]) -> None:
    """
    Write per-table column profiles as CSV and JSON.

    Args:
        run: Completed profiling run
        output: Output directory mapping
    """
    if not run.column_profiles:
        return

    directory = output["column_profiles"]
    combined: List[pd.DataFrame] = []

    for table, profile_df in run.column_profiles.items():
        _write_csv(profile_df, directory / f"{table}_columns.csv")
        _write_json(
            profile_df.to_dict(orient="records"),
            directory / f"{table}_columns.json",
        )
        combined.append(profile_df)

    if combined:
        _write_csv(
            pd.concat(combined, ignore_index=True),
            directory / "all_columns.csv",
        )
    logger.info("Column profiles written to %s", directory)


def write_quality_results(run: ProfilingRun, output: Dict[str, Path]) -> None:
    """
    Write quality findings: all checks, failures only, per-severity
    splits and per-table breakdowns.

    Args:
        run: Completed profiling run
        output: Output directory mapping
    """
    if run.quality_results.empty:
        return

    directory = output["quality_results"]
    results = run.quality_results

    _write_csv(results, directory / "quality_results.csv")
    _write_json(results.to_dict(orient="records"), directory / "quality_results.json")

    failures = results[results["failed_records"] > 0]
    _write_csv(failures, directory / "quality_failures.csv")

    for level in Severity:
        subset = failures[failures["severity"] == level.value]
        if not subset.empty:
            _write_csv(
                subset,
                directory / f"failures_{level.value.lower()}.csv",
            )

    for table, table_results in results.groupby("table_name"):
        _write_csv(table_results, directory / f"{table}_quality.csv")

    if not run.outliers.empty:
        _write_csv(run.outliers, directory / "outliers.csv")

    if not run.category_distribution.empty:
        _write_csv(
            run.category_distribution,
            directory / "category_distribution.csv",
        )

    logger.info("Quality results written to %s", directory)


def write_relationship_results(run: ProfilingRun, output: Dict[str, Path]) -> None:
    """
    Write referential integrity results.

    Args:
        run: Completed profiling run
        output: Output directory mapping
    """
    if run.referential_integrity.empty:
        return

    directory = output["relationship_results"]
    _write_csv(run.referential_integrity, directory / "referential_integrity.csv")
    _write_json(
        run.referential_integrity.to_dict(orient="records"),
        directory / "referential_integrity.json",
    )
    logger.info("Relationship results written to %s", directory)


def write_final_reports(run: ProfilingRun, output: Dict[str, Path]) -> None:
    """
    Write the consolidated data quality report as CSV, JSON and HTML.

    Args:
        run: Completed profiling run
        output: Output directory mapping
    """
    directory = output["reports"]

    if not run.quality_results.empty:
        _write_csv(run.quality_results, directory / "data_quality_report.csv")

    payload: Dict[str, Any] = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": run.summary,
        "quality_scores": run.quality_scores.to_dict(orient="records"),
        "table_profiles": run.table_profiles.to_dict(orient="records"),
        "quality_results": run.quality_results.to_dict(orient="records"),
        "referential_integrity": run.referential_integrity.to_dict(orient="records"),
        "outliers": run.outliers.to_dict(orient="records"),
        "category_distribution": run.category_distribution.to_dict(orient="records"),
        "tables_discovered": run.tables_discovered,
        "tables_missing": run.tables_missing,
        "load_errors": run.load_errors,
    }
    _write_json(payload, directory / "data_quality_report.json")

    if not run.quality_scores.empty:
        _write_csv(run.quality_scores, directory / "quality_scores.csv")

    _write_json(run.summary, directory / "profiling_summary.json")
    _write_html_report(run, directory / "data_quality_report.html")
    logger.info("Final reports written to %s", directory)


def _severity_badge(severity: str) -> str:
    """Return an inline-styled HTML badge for a severity level."""
    colours = {
        Severity.CRITICAL.value: "#b3001b",
        Severity.HIGH.value: "#d9534f",
        Severity.MEDIUM.value: "#e0a800",
        Severity.LOW.value: "#5bc0de",
        Severity.INFO.value: "#6c757d",
    }
    colour = colours.get(severity, "#6c757d")
    return (
        f'<span style="background:{colour};color:#fff;padding:2px 8px;'
        f'border-radius:10px;font-size:11px;font-weight:600">{severity}</span>'
    )


def _df_to_html(df: pd.DataFrame, empty_message: str) -> str:
    """
    Render a DataFrame as an HTML table.

    Args:
        df: Data to render
        empty_message: Text shown when the frame is empty

    Returns:
        str: HTML fragment
    """
    if df.empty:
        return f'<p class="ok">{empty_message}</p>'
    return df.to_html(index=False, escape=False, border=0, classes="grid")


def _write_html_report(run: ProfilingRun, path: Path) -> None:
    """
    Generate a human-readable HTML quality report.

    Args:
        run: Completed profiling run
        path: Destination file path
    """
    summary = run.summary
    score = summary.get("overall_quality_score", 0.0)
    score_colour = (
        "#2d6a2d" if score >= 90 else
        "#e0a800" if score >= 75 else
        "#b3001b"
    )
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    results = run.quality_results
    failures = results[results["failed_records"] > 0] if not results.empty else results

    def section_table(severity: str) -> str:
        subset = failures[failures["severity"] == severity] if not failures.empty else failures
        cols = ["table_name", "column_name", "check_type", "description",
                "failed_records", "failure_percentage", "sample_values"]
        available = [c for c in cols if c in subset.columns]
        return _df_to_html(
            subset[available] if not subset.empty else subset,
            f"No {severity.lower()} severity issues found.",
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Retail ETL — Data Quality Report</title>
<style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
        margin:0;padding:0;background:#f4f6f9;color:#222}}
  header{{background:#1a3a5c;color:#fff;padding:24px 40px}}
  header h1{{margin:0;font-size:22px}}
  header p{{margin:4px 0 0;font-size:13px;opacity:.8}}
  main{{max-width:1280px;margin:32px auto;padding:0 24px}}
  .cards{{display:flex;flex-wrap:wrap;gap:16px;margin-bottom:32px}}
  .card{{background:#fff;border-radius:8px;padding:20px 28px;
         box-shadow:0 1px 4px rgba(0,0,0,.1);min-width:140px;flex:1}}
  .card .value{{font-size:28px;font-weight:700;line-height:1}}
  .card .label{{font-size:12px;color:#666;margin-top:6px}}
  .score{{color:{score_colour}}}
  h2{{font-size:16px;border-bottom:2px solid #1a3a5c;padding-bottom:6px;
       margin-top:36px;margin-bottom:12px;color:#1a3a5c}}
  .grid{{width:100%;border-collapse:collapse;font-size:13px}}
  .grid th{{background:#1a3a5c;color:#fff;padding:8px 12px;text-align:left}}
  .grid td{{padding:7px 12px;border-bottom:1px solid #e8ecef}}
  .grid tr:nth-child(even){{background:#f8f9fb}}
  .ok{{color:#2d6a2d;font-style:italic}}
  footer{{text-align:center;font-size:12px;color:#999;padding:32px 0}}
  @media(max-width:640px){{.cards{{flex-direction:column}}}}
</style>
</head>
<body>
<header>
  <h1>Retail ETL — Data Quality Report</h1>
  <p>Generated: {generated} &nbsp;|&nbsp; Stage: Data Profiling &amp; Quality Assessment</p>
</header>
<main>

<h2>Executive Summary</h2>
<div class="cards">
  <div class="card"><div class="value score">{score:.1f}%</div><div class="label">Overall Quality Score</div></div>
  <div class="card"><div class="value">{summary.get('tables_profiled', 0)}</div><div class="label">Tables Profiled</div></div>
  <div class="card"><div class="value">{summary.get('total_records', 0):,}</div><div class="label">Total Records</div></div>
  <div class="card"><div class="value">{summary.get('total_quality_checks', 0):,}</div><div class="label">Quality Checks</div></div>
  <div class="card"><div class="value" style="color:#b3001b">{summary.get('critical_issues', 0)}</div><div class="label">Critical Issues</div></div>
  <div class="card"><div class="value" style="color:#d9534f">{summary.get('high_issues', 0)}</div><div class="label">High Issues</div></div>
  <div class="card"><div class="value" style="color:#e0a800">{summary.get('medium_issues', 0)}</div><div class="label">Medium Issues</div></div>
  <div class="card"><div class="value" style="color:#5bc0de">{summary.get('low_issues', 0)}</div><div class="label">Low Issues</div></div>
</div>

<h2>Quality Scores by Table</h2>
{_df_to_html(run.quality_scores, "No score data.")}

<h2>Table Summary</h2>
{_df_to_html(run.table_profiles[['table_name','row_count','column_count','duplicate_row_count','total_null_values','completeness_pct']] if not run.table_profiles.empty else run.table_profiles, "No table data.")}

<h2>Critical Issues</h2>
{section_table(Severity.CRITICAL.value)}

<h2>High Severity Issues</h2>
{section_table(Severity.HIGH.value)}

<h2>Medium Severity Issues</h2>
{section_table(Severity.MEDIUM.value)}

<h2>Low Severity Issues</h2>
{section_table(Severity.LOW.value)}

<h2>Referential Integrity</h2>
{_df_to_html(run.referential_integrity, "No relationship data.")}

<h2>Potential Outliers</h2>
{_df_to_html(run.outliers[['table_name','column_name','lower_bound','upper_bound','outlier_count','outlier_percentage','sample_outliers']] if not run.outliers.empty else run.outliers, "No outliers detected.")}

</main>
<footer>Retail ETL Pipeline &mdash; Data Profiling Stage &mdash; {generated}</footer>
</body>
</html>"""

    try:
        path.write_text(html, encoding="utf-8")
        logger.info("HTML report written to %s", path)
    except OSError as exc:
        logger.error("Failed to write HTML report: %s", exc)


def write_findings_doc(run: ProfilingRun, docs_dir: Path) -> None:
    """
    Update docs/data_quality_findings.md with the findings from
    this profiling run. Recommended actions are documented but no
    data is changed.

    Args:
        run: Completed profiling run
        docs_dir: docs/ directory path
    """
    docs_dir.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = run.quality_results
    failures = results[results["failed_records"] > 0] if not results.empty else results
    summary = run.summary

    lines = [
        "# Data Quality Findings",
        "",
        f"> Auto-generated: {generated}  ",
        "> **This file documents issues only. No data has been modified.**",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Tables profiled | {summary.get('tables_profiled', 0)} |",
        f"| Total records | {summary.get('total_records', 0):,} |",
        f"| Quality checks | {summary.get('total_quality_checks', 0):,} |",
        f"| Failed checks | {summary.get('failed_checks', 0):,} |",
        f"| Critical issues | {summary.get('critical_issues', 0)} |",
        f"| High issues | {summary.get('high_issues', 0)} |",
        f"| Medium issues | {summary.get('medium_issues', 0)} |",
        f"| Low issues | {summary.get('low_issues', 0)} |",
        f"| Overall quality score | {summary.get('overall_quality_score', 0.0):.2f}% |",
        "",
    ]

    for severity in [
        Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW
    ]:
        subset = (
            failures[failures["severity"] == severity.value]
            if not failures.empty else failures
        )
        if subset.empty:
            continue

        lines.append(f"## {severity.value} Issues")
        lines.append("")
        lines.append(
            "| Table | Column | Check | Failed | % | Sample | Recommended Action |"
        )
        lines.append("|-------|--------|-------|--------|---|--------|-------------------|")

        for row in subset.itertuples(index=False):
            action = _recommended_action(row.check_type)
            sample = str(row.sample_values).replace("|", "/")[:60]
            lines.append(
                f"| {row.table_name} | {row.column_name} | {row.check_type} "
                f"| {row.failed_records} | {row.failure_percentage:.1f}% "
                f"| {sample} | {action} |"
            )
        lines.append("")

    if not run.referential_integrity.empty:
        failed_ri = run.referential_integrity[
            run.referential_integrity["status"] == "FAIL"
        ]
        if not failed_ri.empty:
            lines.append("## Referential Integrity Failures")
            lines.append("")
            lines.append(
                "| Relationship | Orphans | Integrity % | Sample |"
            )
            lines.append("|-------------|---------|-------------|--------|")
            for row in failed_ri.itertuples(index=False):
                lines.append(
                    f"| {row.child_table}.{row.child_column} → "
                    f"{row.parent_table}.{row.parent_column} "
                    f"| {row.orphan_count} | {row.integrity_percentage:.1f}% "
                    f"| {str(row.sample_orphans)[:40]} |"
                )
            lines.append("")

    lines.append("---")
    lines.append(
        "> Issues listed here will be resolved in the **Transformation** phase."
    )

    out_path = docs_dir / "data_quality_findings.md"
    try:
        out_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Findings doc written to %s", out_path)
    except OSError as exc:
        logger.error("Failed to write findings doc: %s", exc)


def _recommended_action(check_type: str) -> str:
    """
    Return a brief recommended action for a check type.

    Args:
        check_type: CheckType value

    Returns:
        str: Short action description for the findings doc
    """
    actions: Dict[str, str] = {
        "NULL_PRIMARY_KEY": "Investigate source system; reject record if unresolvable",
        "DUPLICATE_PRIMARY_KEY": "Deduplicate in transformation using latest record",
        "INVALID_PRIMARY_KEY": "Quarantine to reject/ folder; alert source team",
        "NULL_VALUE": "Apply default or reject in transformation",
        "FOREIGN_KEY": "Investigate orphans; default to null FK or reject",
        "DATA_TYPE_MISMATCH": "Cast to expected type in transformation",
        "INVALID_DATE": "Parse with fallback formats; reject if unresolvable",
        "FUTURE_DATE": "Flag for source team review; exclude from aggregations",
        "DATE_OUT_OF_RANGE": "Flag for source team review",
        "DATE_SEQUENCE": "Investigate upstream; swap or reject in transformation",
        "NEGATIVE_VALUE": "Investigate; apply ABS or reject in transformation",
        "ZERO_VALUE": "Apply business default or reject",
        "INVALID_EMAIL": "Flag for outreach team; strip or nullify in transformation",
        "INVALID_PHONE": "Normalise format in transformation",
        "INVALID_CATEGORY": "Map to closest valid value or NULL in transformation",
        "BUSINESS_RULE": "Investigate root cause; exclude from reporting until resolved",
        "POTENTIAL_OUTLIER": "Review manually; do not auto-correct",
        "LEADING_OR_TRAILING_WHITESPACE": "Trim in transformation",
        "MULTIPLE_SPACES": "Normalise spaces in transformation",
        "EMPTY_STRING": "Replace with NULL in transformation",
        "EXCESSIVE_LENGTH": "Truncate or investigate source in transformation",
        "DUPLICATE_ROW": "Keep latest record in transformation",
    }
    return actions.get(check_type, "Review in transformation phase")


def generate_all_reports(
    run: ProfilingRun,
    output_dir: Path,
    docs_dir: Path,
) -> None:
    """
    Write every report artefact for a completed profiling run.

    Args:
        run: Completed profiling run
        output_dir: Root output directory (data/profiling)
        docs_dir: Project docs/ directory
    """
    output = ensure_output_dirs(output_dir)
    write_table_profiles(run, output)
    write_column_profiles(run, output)
    write_quality_results(run, output)
    write_relationship_results(run, output)
    write_final_reports(run, output)
    write_findings_doc(run, docs_dir)
    logger.info("All reports written to %s", output_dir)
