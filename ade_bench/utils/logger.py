"""Logging configuration for ADE-Bench."""

import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from ade_bench.config import config


def setup_logger(name: str = "ade_bench", level: str = None) -> logging.Logger:
    """Set up logger with rich formatting.
    
    Args:
        name: Logger name
        level: Logging level (defaults to config.log_level)
        
    Returns:
        Configured logger instance
    """
    level = level or config.log_level
    
    # Create console for rich output
    console = Console(stderr=True)
    
    # Configure handler
    handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
    )
    
    # Set format
    handler.setFormatter(
        logging.Formatter(
            fmt="%(message)s",
            datefmt="[%Y-%m-%d %H:%M:%S]",
        )
    )
    
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


# Global logger instance
logger = setup_logger()