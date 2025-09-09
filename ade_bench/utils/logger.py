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
    message_transforms = {
        ## SETUP
        "Capturing initial file snapshot...": "* · ·  Capturing initial file snapshot...",''
        "Captured snapshot": "* · ·  Captured snapshot.",
        "Running setup script": "* · ·  Running setup script...",
        "Setup script completed": "* · ·  Setup script completed.",
        "Diffing the setup changes...": "* · ·  Diffing the setup changes...",
        "Captured setup diffs:": "* · ·  Captured setup diffs:",
        "Starting agent...": "✓ * ·  Starting agent...",
        "Calling agent:": "✓ * ·  Calling agent:",
        ## AGENT
        "Agent returned response": "✓ * ·  Agent returned response...",
        "Agent response:": "✓ * ·  Agent response:",
        "Diffing the agent changes...": "✓ * ·  Diffing the agent changes...",
        "Captured agent diffs:": "✓ ✓ ·  Captured agent diffs:",
        ## EVAL
        "Generating solution tests": "✓ ✓ *  Generating solution tests...",
        "Executing test script": "✓ ✓ *  Executing test script...",
        "dbt test summary:": "✓ ✓ ✓  dbt test summary:",

        ## SEED
        "Extracting tables:": "✓ ✓ ⤴  Extracting tables:",
        "Exported": "✓ ✓ ⤴  Exported",
        "Generated _no-op.txt file:": "✓ ✓ ⤴  Generated _no-op.txt file:",
    }

    message_parts = message.split("|||")
    
    # Transform the first part if it exists in mapping
    if message_parts[0] in message_transforms:
        message_parts[0] = message_transforms[message_parts[0]]
    
    # Rejoin the parts
    message = " ".join(message_parts)
        
    formatted_message = f"{timestamp.strftime('%H:%M:%S'):<8} | {task:<40} | {stage.upper():<12} | {message}"
    logger.info(formatted_message)


logger = setup_logger(__name__)
