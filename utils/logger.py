"""
===========================================
Utilities - Logging Configuration
===========================================
Centralised logger factory for the ETL pipeline.
Writes structured logs to logs/extract.log and
surfaces warnings/errors on the console.
"""

import logging
from pathlib import Path
from typing import Optional

# Project root is one level above utils/
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
LOG_DIR: Path = PROJECT_ROOT / "logs"
LOG_FILE: Path = LOG_DIR / "extract.log"

PROFILING_LOG_FILE: Path = LOG_DIR / "profiling.log"

_FILE_FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)-28s | %(message)s"
_CONSOLE_FORMAT: str = "%(levelname)s | %(message)s"
_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


def get_logger(
    name: str = "retail_etl.extract",
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """
    Return a configured logger. Safe to call repeatedly:
    handlers are attached only once per logger name.

    Args:
        name: Logger name (use module __name__ for traceability)
        log_file: Destination log file. Defaults to logs/extract.log.

    Returns:
        logging.Logger: Logger writing to the requested log file
    """
    logger = logging.getLogger(name)

    # Already configured - return as-is to avoid duplicate handlers
    if logger.handlers:
        return logger

    target = log_file if log_file is not None else LOG_FILE
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(target, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(_FILE_FORMAT, _DATE_FORMAT))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter(_CONSOLE_FORMAT))
    logger.addHandler(console_handler)

    # Prevent double-logging through the root logger
    logger.propagate = False
    return logger


def get_profiling_logger(name: str) -> logging.Logger:
    """
    Return a logger that writes to logs/profiling.log.

    Args:
        name: Logger name (use module __name__)

    Returns:
        logging.Logger: Logger for the profiling stage
    """
    return get_logger(name, log_file=PROFILING_LOG_FILE)
