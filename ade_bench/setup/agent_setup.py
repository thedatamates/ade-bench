"""
Agent-specific setup functions for copying configuration files and other agent resources.
"""

from ..utils.logger import logger
from ..terminal.docker_compose_manager import DockerComposeManager
from ..agents.agent_name import AgentName
from ..utils.logger import log_harness_info

def _setup_claude_config(terminal, task_id: str, trial_handler) -> None:
    """Setup Claude-specific configuration files."""
    claude_config_path = trial_handler.shared_config_path / "CLAUDE.md"
    if claude_config_path.exists():
        terminal.copy_to_container(
            paths=claude_config_path,
            container_dir=str(DockerComposeManager.CONTAINER_APP_DIR),
            container_filename="CLAUDE.md"
        )
    else:
        logger.warning(f"Claude configuration file not found at {claude_config_path}")


def setup_agent_config(terminal, task_id: str, trial_handler, logger) -> None:
    """Setup agent-specific configuration files and resources."""

    agent_name = trial_handler.agent_name

    if agent_name == AgentName.CLAUDE_CODE:
        log_harness_info(logger, task_id, "setup", "Migrating agent config files...")
        _setup_claude_config(terminal, task_id, trial_handler)
