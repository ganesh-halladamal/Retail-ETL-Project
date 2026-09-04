"""
===========================================
Retail ETL Project - Configuration Module
===========================================
This module loads environment variables from .env file
and provides database configuration for the ETL pipeline.

Requires: MySQL 8.0.16+
"""

import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL

# Load environment variables from .env file
load_dotenv()


def _get_env(key: str, default: str = "") -> str:
    """
    Get environment variable, treating empty string same as unset.

    Args:
        key: Environment variable name
        default: Fallback value if key is unset or empty

    Returns:
        str: The value or default
    """
    value = os.getenv(key, "")
    return value if value else default


def get_db_config() -> dict:
    """
    Returns database configuration dictionary
    loaded from environment variables.

    Returns:
        dict: Database connection parameters

    Raises:
        ValueError: If DB_PORT is not a valid integer
    """
    port_str = _get_env("DB_PORT", "3306")
    try:
        port = int(port_str)
    except ValueError:
        raise ValueError(
            f"DB_PORT must be a valid integer, got: '{port_str}'"
        )

    db_config: dict = {
        "host": _get_env("DB_HOST", "localhost"),
        "port": port,
        "user": _get_env("DB_USER", "etl_user"),
        "password": _get_env("DB_PASSWORD", ""),
        "source_db": _get_env("SOURCE_DB", "retail_oltp"),
        "warehouse_db": _get_env("WAREHOUSE_DB", "retail_dwh"),
    }
    return db_config


def get_connection_string(db_name: str) -> URL:
    """
    Generates SQLAlchemy connection URL for MySQL.
    Uses URL.create() for proper credential encoding
    (handles special chars like @, :, /, # in passwords).

    Args:
        db_name: Name of the database to connect to

    Returns:
        sqlalchemy.engine.URL: Safe connection URL object
    """
    config = get_db_config()
    connection_url: URL = URL.create(
        drivername="mysql+mysqlconnector",
        username=config["user"],
        password=config["password"],
        host=config["host"],
        port=config["port"],
        database=db_name,
    )
    return connection_url


# ===========================================
# Configuration constants
# ===========================================
PROJECT_NAME: str = "Retail ETL Project"
VERSION: str = "1.0.0"
