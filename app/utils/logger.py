from loguru import logger
import sys
from pathlib import Path

def setup_logger():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger.remove()
    logger.add(sys.stdout, format="{time} | {level} | {message}", colorize=True)
    logger.add("logs/gateway.json", rotation="10 MB", retention="7 days", serialize=True, enqueue=True)
    return logger
