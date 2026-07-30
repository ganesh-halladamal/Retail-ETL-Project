"""
===========================================
Retail ETL Project - Configuration Module
===========================================
This module loads environment variables from .env file
and provides database configuration for the ETL pipeline.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_db_config() -> dict:
    """
    Returns database configuration dictionary
    loaded from environment variables.

    Returns:
        dict: Database connection parameters
    """
    db_config: dict = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "source_db": os.getenv("SOURCE_DB", ""),
        "warehouse_db": os.getenv("WAREHOUSE_DB", ""),
    }
    return db_config


def get_connection_string(db_name: str) -> str:
    """
    Generates SQLAlchemy connection string for MySQL.

    Args:
        db_name: Name of the database to connect to

    Returns:
        str: SQLAlchemy-compatible connection URL
    """
    config = get_db_config()
    connection_string: str = (
        f"mysql+mysqlconnector://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{db_name}"
    )
    return connection_string


# ===========================================
# Configuration constants
# ===========================================
PROJECT_NAME: str = "Retail ETL Project"
VERSION: str = "1.0.0"
