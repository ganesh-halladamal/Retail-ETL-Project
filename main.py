"""
===========================================
Retail ETL Project - Main Entry Point
===========================================
This is the main execution file for the Retail ETL Pipeline.
Currently initializes the project and verifies configuration.
"""

from colorama import init, Fore, Style
from config import get_db_config, PROJECT_NAME, VERSION

# Initialize colorama for colored terminal output
init(autoreset=True)


def main() -> None:
    """
    Main function to initialize and run the ETL pipeline.
    Currently displays project initialization status.
    """
    print(Fore.CYAN + "=" * 43)
    print(Fore.GREEN + f"       {PROJECT_NAME} v{VERSION}")
    print(Fore.GREEN + "  Project Initialized Successfully")
    print(Fore.CYAN + "=" * 43)

    # Load configuration from config module (single source of truth)
    try:
        db_config = get_db_config()
    except ValueError as e:
        print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} Configuration error: {e}")
        return

    # Display loaded configuration
    print(f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} Database Host: {db_config['host']}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Database Port: {db_config['port']}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Source DB: {db_config['source_db']}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Warehouse DB: {db_config['warehouse_db']}")
    print(f"\n{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Project setup complete. Ready for ETL development.\n")


if __name__ == "__main__":
    main()
