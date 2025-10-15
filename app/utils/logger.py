"""
Custom logger setup using Loguru.
Handles console output and file-based rotation for persistent logs.
"""

from loguru import logger
import sys
from pathlib import Path


def setup_logger():
    """Configure Loguru logger with console and file sinks."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        colorize=True,
    )
    logger.add("logs/gateway.log", rotation="1 MB", retention="7 days", enqueue=True)
    return logger
