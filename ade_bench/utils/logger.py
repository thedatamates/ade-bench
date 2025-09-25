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

    # Map certain messages to transformed versions for consistent logging
    # The delimiters ||| is used to split messages with custom logging
    prefixes = {
        ## SETUP

        ## SETUP STAGE
        "Capturing snapshot...": "* · ·  ",
        "Captured snapshot.": "* · ·  ",
        "Starting task setup...": "* · ·  ",
        "Setting up DuckDB database...": "* · ·  ",
        "Setting up Snowflake database at": "* · ·  ",
        "Snowflake setup complete.": "* · ·  ",
        "Setting up dbt project...": "* · ·  ",
        "Running migrations...": "* · ·  ",
        "Migration script complete": "* · ·  ",
        "Running setup script...": "* · ·  ",
        "Setup script complete.": "* · ·  ",
        "Migrating agent config files...": "* · ·  ",
        "Diffing the setup changes...": "* · ·  ",
        "Captured setup diffs:": "✓ · ·  ",

        ## AGENT
        "Starting agent...": "✓ * ·  ",
        "Calling agent:": "✓ * ·  ",
        "Agent returned response": "✓ * ·  ",
        "Agent response:": "✓ * ·  ",
        "Diffing the agent changes...": "✓ * ·  ",
        "Captured agent diffs:": "✓ ✓ ·  ",
        ## EVAL
        "Generating solution tests": "✓ ✓ *  ",
        "Executing test script": "✓ ✓ *  ",
        "dbt test summary:": "✓ ✓ ✓  ",

        ## SEED
        "Extracting tables:": "✓ ✓ ⤴  ",
        "Exported": "✓ ✓ ⤴  ",
        "Generated _no-op.txt file:": "✓ ✓ ⤴  ",
        "CSV extraction not supported for db_type:": "✓ ✓ ⤴  ",
    }

    message_parts = message.split("|||")

    # Transform the first part if it exists in mapping
    if message_parts[0] in prefixes:
        message_parts[0] = prefixes[message_parts[0]] + message_parts[0]

    # Rejoin the parts
    message = " ".join(message_parts)

    formatted_message = f"{timestamp.strftime('%H:%M:%S'):<8} | {task:<40} | {stage.upper():<12} | {message}"
    logger.info(formatted_message)


logger = setup_logger(__name__)
