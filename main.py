"""
===========================================
Retail ETL Project - Main Entry Point
===========================================
This is the main execution file for the Retail ETL Pipeline.
Currently initializes the project and verifies configuration.
"""

import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init(autoreset=True)

# Load environment variables from .env file
load_dotenv()


def main() -> None:
    """
    Main function to initialize and run the ETL pipeline.
    Currently displays project initialization status.
    """
    print(Fore.CYAN + "=" * 43)
    print(Fore.GREEN + "       Retail ETL Pipeline")
    print(Fore.GREEN + "  Project Initialized Successfully")
    print(Fore.CYAN + "=" * 43)

    # Display loaded configuration
    db_host: str = os.getenv("DB_HOST", "Not Configured")
    print(f"\n{Fore.YELLOW}[INFO]{Style.RESET_ALL} Database Host: {db_host}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Database Port: {os.getenv('DB_PORT', '3306')}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Source DB: {os.getenv('SOURCE_DB', 'Not Configured')}")
    print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Warehouse DB: {os.getenv('WAREHOUSE_DB', 'Not Configured')}")
    print(f"\n{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Project setup complete. Ready for ETL development.\n")


if __name__ == "__main__":
    main()
