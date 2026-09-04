"""
===========================================
Extract - Database Connection
===========================================
Reusable SQLAlchemy engine for the retail_oltp
source database, with connection pooling and
graceful failure handling.

Credentials are read from .env via config.py -
never hardcoded.
"""

from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from config import get_connection_string, get_db_config
from utils.logger import get_logger

logger = get_logger(__name__)

# Connection pool settings
POOL_SIZE: int = 5
MAX_OVERFLOW: int = 10
POOL_TIMEOUT: int = 30
POOL_RECYCLE: int = 3600  # Recycle connections hourly

# Module-level engine cache (one pool per process)
_engine: Optional[Engine] = None


class DatabaseConnectionError(Exception):
    """Raised when the source database cannot be reached."""


def get_engine() -> Engine:
    """
    Return a pooled SQLAlchemy engine for the source database.
    The engine is created once and reused for all extractions.

    Returns:
        Engine: Pooled SQLAlchemy engine

    Raises:
        DatabaseConnectionError: If the engine cannot be created
    """
    global _engine

    if _engine is not None:
        return _engine

    config = get_db_config()
    source_db = config["source_db"]

    try:
        _engine = create_engine(
            get_connection_string(source_db),
            pool_size=POOL_SIZE,
            max_overflow=MAX_OVERFLOW,
            pool_timeout=POOL_TIMEOUT,
            pool_recycle=POOL_RECYCLE,
            pool_pre_ping=True,  # Validate connections before use
        )
    except SQLAlchemyError as exc:
        logger.error("Failed to create engine for '%s': %s", source_db, exc)
        raise DatabaseConnectionError(
            f"Could not create engine for database '{source_db}': {exc}"
        ) from exc

    logger.info(
        "Engine created for '%s' (pool_size=%d, max_overflow=%d)",
        source_db, POOL_SIZE, MAX_OVERFLOW,
    )
    return _engine


def test_connection() -> bool:
    """
    Verify the source database is reachable.

    Returns:
        bool: True if a test query succeeds, False otherwise
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except (DatabaseConnectionError, SQLAlchemyError) as exc:
        logger.error("Connection test failed: %s", exc)
        return False

    logger.info("Connection test succeeded.")
    return True


def dispose_engine() -> None:
    """Close all pooled connections and reset the engine cache."""
    global _engine

    if _engine is not None:
        _engine.dispose()
        _engine = None
        logger.info("Engine disposed; connection pool closed.")
