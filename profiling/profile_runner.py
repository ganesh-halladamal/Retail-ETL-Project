"""
===========================================
Profiling - Master Runner
===========================================
Entry point for Phase 5: Data Profiling and
Data Quality Assessment.

Usage
-----
Run all tables:
    python -m profiling.profile_runner
    python profiling/profile_runner.py

Run a single table:
    python -m profiling.profile_runner --table customers

Custom directories:
    python -m profiling.profile_runner \\
        --input-dir data/raw \\
        --output-dir data/profiling \\
        --verbose

Exit codes
----------
0  All tables profiled with zero CRITICAL issues.
1  CRITICAL issues found or no tables could be loaded.
2  Argument / configuration error.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from colorama import Fore, Style, init

from profiling.profiler import (
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    PROJECT_ROOT,
    ProfilingRun,
    run_profiling,
)
from profiling.report_generator import generate_all_reports
from profiling.quality_rules import Severity
from utils.logger import get_profiling_logger, PROFILING_LOG_FILE

init(autoreset=True)
logger = get_profiling_logger(__name__)

DOCS_DIR: Path = PROJECT_ROOT / "docs"


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv)

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog="profile_runner",
        description="Retail ETL — Data Profiling & Quality Assessment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m profiling.profile_runner\n"
            "  python -m profiling.profile_runner --table customers\n"
            "  python -m profiling.profile_runner --verbose\n"
        ),
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing raw CSV extracts (default: data/raw)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Root output directory for profiling results (default: data/profiling)",
    )
    parser.add_argument(
        "--table",
        type=str,
        default=None,
        metavar="TABLE",
        help="Profile a single table only (e.g. --table customers)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print full findings table to the console",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Skip the HTML report (faster for automated runs)",
    )
    return parser.parse_args(argv)


def print_banner() -> None:
    """Print the profiling stage banner."""
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + "  Retail ETL Pipeline — Phase 5")
    print(Fore.GREEN + "  Data Profiling & Quality Assessment")
    print(Fore.CYAN + "=" * 60)
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Log: {PROFILING_LOG_FILE}")
    print()


def print_summary(run: ProfilingRun) -> None:
    """
    Print the profiling summary banner to stdout.

    Args:
        run: Completed profiling run
    """
    s = run.summary
    score = s.get("overall_quality_score", 0.0)
    score_colour = (
        Fore.GREEN if score >= 90 else
        Fore.YELLOW if score >= 75 else
        Fore.RED
    )

    print()
    print(Fore.CYAN + "=" * 45)
    print(Fore.GREEN + "  DATA PROFILING SUMMARY")
    print(Fore.CYAN + "=" * 45)
    print(f"  Tables Profiled  : {s.get('tables_profiled', 0)}/{s.get('tables_expected', 0)}")
    if s.get("tables_missing"):
        print(f"{Fore.YELLOW}  Missing Tables   : {', '.join(s['tables_missing'])}{Style.RESET_ALL}")
    print(f"  Total Records    : {s.get('total_records', 0):,}")
    print(f"  Total Columns    : {s.get('total_columns', 0)}")
    print(f"  Quality Checks   : {s.get('total_quality_checks', 0):,}")
    print(f"  Passed Checks    : {s.get('passed_checks', 0):,}")
    print(f"  Failed Checks    : {s.get('failed_checks', 0):,}")
    print(f"  {Fore.RED}Critical Issues  : {s.get('critical_issues', 0)}{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTRED_EX}High Issues      : {s.get('high_issues', 0)}{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}Medium Issues    : {s.get('medium_issues', 0)}{Style.RESET_ALL}")
    print(f"  {Fore.CYAN}Low Issues       : {s.get('low_issues', 0)}{Style.RESET_ALL}")
    print(f"  {score_colour}Quality Score    : {score:.2f}%{Style.RESET_ALL}")
    print(Fore.CYAN + "=" * 45)
    print()


def print_verbose_findings(run: ProfilingRun) -> None:
    """
    Print the top 30 failures to the console in verbose mode.

    Args:
        run: Completed profiling run
    """
    results = run.quality_results
    failures = results[results["failed_records"] > 0] if not results.empty else results
    if failures.empty:
        print(f"{Fore.GREEN}No failures found.{Style.RESET_ALL}")
        return

    print(f"\n{Fore.CYAN}Top Findings (most severe, first 30):{Style.RESET_ALL}\n")
    cols = [
        "severity", "table_name", "column_name",
        "check_type", "failed_records", "failure_percentage",
    ]
    available = [c for c in cols if c in failures.columns]
    try:
        from tabulate import tabulate
        print(tabulate(
            failures[available].head(30),
            headers="keys",
            tablefmt="github",
            showindex=False,
        ))
    except ImportError:
        print(failures[available].head(30).to_string(index=False))
    print()


def main(argv: Optional[list] = None) -> int:
    """
    Execute the profiling pipeline and return an exit code.

    Args:
        argv: Argument list for testing (defaults to sys.argv)

    Returns:
        int: 0 (clean), 1 (critical issues / no tables), 2 (arg error)
    """
    args = parse_args(argv)

    if not args.input_dir.exists():
        print(
            f"{Fore.RED}[ERROR]{Style.RESET_ALL} "
            f"Input directory not found: {args.input_dir}\n"
            f"Run the extraction layer first: python main.py"
        )
        return 2

    print_banner()
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Input  : {args.input_dir}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Output : {args.output_dir}")
    if args.table:
        print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Table  : {args.table}")
    print()

    logger.info(
        "profile_runner started | input=%s | output=%s | table=%s",
        args.input_dir, args.output_dir, args.table or "ALL",
    )

    run = run_profiling(
        input_dir=args.input_dir,
        only_table=args.table,
    )

    if not run.tables_discovered:
        print(
            f"{Fore.RED}[FAILED]{Style.RESET_ALL} No tables loaded. "
            f"Check that extraction has been run first."
        )
        return 1

    generate_all_reports(run, args.output_dir, DOCS_DIR)

    if args.verbose:
        print_verbose_findings(run)

    print_summary(run)

    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Reports : {args.output_dir}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} HTML    : "
          f"{args.output_dir / 'reports' / 'data_quality_report.html'}")

    critical = run.summary.get("critical_issues", 0)
    if critical:
        print(
            f"\n{Fore.RED}[WARNING]{Style.RESET_ALL} "
            f"{critical} CRITICAL issue(s) found. "
            f"Review before proceeding to transformation.\n"
        )
        return 1

    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Profiling complete. "
          f"No critical issues.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
