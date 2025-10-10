"""
Agent-specific setup functions for copying configuration files and other agent resources.
"""

from ..utils.logger import logger
from ..terminal.docker_compose_manager import DockerComposeManager
from ..agents.agent_name import AgentName
from ..utils.logger import log_harness_info

def _copy_config_file(terminal, trial_handler, config_filename: str, container_filename: str = None) -> None:
    """Helper to copy a configuration file to the container."""
    if container_filename is None:
        container_filename = config_filename

    config_path = trial_handler.shared_config_path / config_filename
    if config_path.exists():
        terminal.copy_to_container(
            paths=config_path,
            container_dir=str(DockerComposeManager.CONTAINER_APP_DIR),
            container_filename=container_filename
        )
    else:
        logger.warning(f"Configuration file not found at {config_path}")


def setup_agent_config(terminal, task_id: str, trial_handler, logger) -> None:
    """Setup agent-specific configuration files and resources."""

    agent_name = trial_handler.agent_name

    log_harness_info(logger, task_id, "setup", "Migrating agent config files...")

    if agent_name == AgentName.CLAUDE_CODE:
        _copy_config_file(terminal, trial_handler, "CLAUDE.md")
    elif agent_name == AgentName.GEMINI_CLI:
        _copy_config_file(terminal, trial_handler, "GEMINI.md")
    elif agent_name == AgentName.OPENAI_CODEX:
        _copy_config_file(terminal, trial_handler, "AGENTS.md")
    
    # Install agent-specific scripts for installed agents
    if agent_name in [AgentName.CLAUDE_CODE, AgentName.MACRO]:
        install_agent(terminal, agent_name, logger, task_id)
        
def install_agent(terminal, agent_name, logger, task_id):
    """Install an agent in interactive mode (without a tmux session)"""
    from pathlib import Path
    import os
    
    log_harness_info(logger, task_id, "setup", f"Installing {agent_name.value} agent...")
    
    # Get the agent's install script
    script_path = None
    if agent_name == AgentName.MACRO:
        # Determine which Macro setup script to use
        if os.environ.get("MACRO_BINARY_PATH"):
            script_path = Path(__file__).parent.parent / "agents/installed_agents/macro/macro-setup-local.sh"
        else:
            script_path = Path(__file__).parent.parent / "agents/installed_agents/macro/macro-setup.sh"
    elif agent_name == AgentName.CLAUDE_CODE:
        script_path = Path(__file__).parent.parent / "agents/installed_agents/claude_code/claude-code-setup.sh"
    
    if not script_path or not script_path.exists():
        log_harness_info(logger, task_id, "setup", f"Agent installation script not found: {script_path}")
        return
    
    # Copy script to container
    terminal.copy_to_container(
        paths=script_path,
        container_dir="/installed-agent",
        container_filename="install-agent.sh"
    )
    
    # Set up environment variables if needed
    env_vars = {}
    if agent_name == AgentName.MACRO and "MACRO_API_KEY" in os.environ:
        env_vars["MACRO_PLATFORM_API_KEY"] = os.environ["MACRO_API_KEY"]
    elif agent_name == AgentName.CLAUDE_CODE and "ANTHROPIC_API_KEY" in os.environ:
        env_vars["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_API_KEY"]
    
    # Create env setup file if we have variables to set
    if env_vars:
        env_setup_content = "\n".join([f"export {key}='{value}'" for key, value in env_vars.items()])
        terminal.container.exec_run(
            ["sh", "-c", f"echo '{env_setup_content}' > /installed-agent/setup-env.sh"]
        )
        terminal.container.exec_run(["chmod", "+x", "/installed-agent/setup-env.sh"])
        
        # Source the env file
        terminal.container.exec_run(["sh", "-c", "source /installed-agent/setup-env.sh"])
    
    # Make install script executable and run it
    terminal.container.exec_run(["chmod", "+x", "/installed-agent/install-agent.sh"])
    result = terminal.container.exec_run(["bash", "/installed-agent/install-agent.sh"])
    
    if result.exit_code != 0:
        log_harness_info(logger, task_id, "setup", f"Agent installation failed: {result.output.decode('utf-8')}")
    else:
        log_harness_info(logger, task_id, "setup", f"Agent {agent_name.value} installed successfully")
