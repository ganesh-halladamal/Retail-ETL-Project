"""
===========================================
Retail ETL Project - Main Entry Point
===========================================
Runs the extraction layer end to end:

    1. Verify the source database connection
    2. Extract every transactional table
    3. Save raw CSV snapshots to data/raw/
    4. Print an extraction summary

Transformation and warehouse loading are not
part of this stage.
"""

import sys

from colorama import Fore, Style, init
from tabulate import tabulate

from config import PROJECT_NAME, VERSION, get_db_config
from extract.extractor import close, extract_all, get_extraction_summary
from utils.logger import LOG_FILE

# Initialize colorama for colored terminal output
init(autoreset=True)


def print_banner() -> None:
    """Print the project banner and resolved database configuration."""
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + f"  {PROJECT_NAME} v{VERSION} - Extraction Layer")
    print(Fore.CYAN + "=" * 60)

    config = get_db_config()
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Host:         {config['host']}:{config['port']}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Source DB:    {config['source_db']}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Log file:     {LOG_FILE}")
    print()


def main() -> int:
    """
    Execute the extraction pipeline.

    Returns:
        int: 0 when every table was extracted, 1 otherwise
    """
    try:
        config = get_db_config()
    except ValueError as exc:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Configuration error: {exc}")
        return 1

    print_banner()
    print(Fore.CYAN + "Extracting source tables..." + Style.RESET_ALL)

    data = extract_all(save_csv=True)
    close()

    if not data:
        print(
            f"\n{Fore.RED}[FAILED]{Style.RESET_ALL} No tables extracted. "
            f"Check {LOG_FILE} for details."
        )
        return 1

    summary = get_extraction_summary(data)
    print(f"\n{Fore.CYAN}Extraction Summary{Style.RESET_ALL}")
    print(tabulate(summary, headers="keys", tablefmt="github", showindex=False))

    total_tables = 12
    total_rows = int(summary["rows"].sum())
    print(
        f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} Tables extracted: "
        f"{len(data)}/{total_tables}"
    )
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Total rows:       {total_rows:,}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} CSV output:       data/raw/")

    if len(data) < total_tables:
        print(
            f"\n{Fore.YELLOW}[PARTIAL]{Style.RESET_ALL} Some tables failed. "
            f"See {LOG_FILE}.\n"
        )
        return 1

    print(f"\n{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Extraction completed.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
