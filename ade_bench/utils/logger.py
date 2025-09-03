import logging
from datetime import datetime
from typing import Optional


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger


def log_harness_info(
    logger: logging.Logger,
    task: str,
    stage: str,
    message: str,
    timestamp: Optional[datetime] = None
) -> None:
    """
    Centralized info logging function for the harness.
    
    Args:
        logger: The logger instance to use
        task: The task being run
        stage: The task stage (setup, agent run, test, cleanup)
        message: The log message
        timestamp: Optional timestamp, defaults to current time
    """
    if timestamp is None:
        timestamp = datetime.now()
        
    formatted_message = f"{timestamp.strftime('%H:%M:%S'):<8} | {task:<40} | {stage.upper():<12} | > {message}"
    logger.info(formatted_message)


logger = setup_logger(__name__)
