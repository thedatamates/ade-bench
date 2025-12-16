"""
Agent-specific setup functions for copying configuration files and other agent resources.
"""

import tempfile
from pathlib import Path
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


def _copy_claude_config(terminal, trial_handler, use_skills: bool) -> None:
    """Helper to copy CLAUDE.md config file, optionally removing skills section."""
    config_path = trial_handler.shared_config_path / "CLAUDE.md"
    if not config_path.exists():
        logger.warning(f"Configuration file not found at {config_path}")
        return

    # Read the config file
    with open(config_path, 'r') as f:
        content = f.read()

    # If skills are disabled, remove the "Available Skills" section
    if not use_skills:
        lines = content.split('\n')
        filtered_lines = []
        skip_section = False
        
        for i, line in enumerate(lines):
            # Check if we're at the start of the Available Skills section
            if line.strip() == "## Available Skills":
                skip_section = True
                continue
            
            # Check if we've reached the next section (starts with ##)
            if skip_section and line.strip().startswith("## ") and "Available Skills" not in line:
                skip_section = False
            
            # Only add lines if we're not in the skills section
            if not skip_section:
                filtered_lines.append(line)
        
        content = '\n'.join(filtered_lines)
        # Remove any extra blank lines that might have been left
        while '\n\n\n' in content:
            content = content.replace('\n\n\n', '\n\n')

    # Write to a temporary file and copy to container
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_file.flush()
        tmp_path = Path(tmp_file.name)
    
    try:
        terminal.copy_to_container(
            paths=tmp_path,
            container_dir=str(DockerComposeManager.CONTAINER_APP_DIR),
            container_filename="CLAUDE.md"
        )
    finally:
        # Clean up temp file
        tmp_path.unlink()


def _copy_skills_directory(terminal, trial_handler) -> None:
    """Helper to copy the skills directory to the container's .claude/skills directory."""
    skills_path = trial_handler.shared_config_path / "skills"
    if skills_path.exists() and skills_path.is_dir():
        # Create .claude/skills directory in the container first
        claude_skills_dir = DockerComposeManager.CONTAINER_APP_DIR / ".claude/skills"
        terminal.container.exec_run(["mkdir", "-p", str(claude_skills_dir)])
        
        # Copy skills directory contents to .claude/skills in the container
        terminal.copy_to_container(
            paths=skills_path,
            container_dir=str(claude_skills_dir)
        )
    else:
        logger.debug(f"Skills directory not found at {skills_path}, skipping skill setup")
        
def setup_agent_config(terminal, task_id: str, trial_handler, logger, use_skills: bool = False) -> None:
    """Setup agent-specific configuration files and resources."""

    agent_name = trial_handler.agent_name

    log_harness_info(logger, task_id, "setup", "Migrating agent config files...")

    if agent_name == AgentName.CLAUDE_CODE:
        _copy_claude_config(terminal, trial_handler, use_skills)
        if use_skills:
            _copy_skills_directory(terminal, trial_handler)
    elif agent_name == AgentName.GEMINI_CLI:
        _copy_config_file(terminal, trial_handler, "GEMINI.md")
    elif agent_name == AgentName.OPENAI_CODEX:
        _copy_config_file(terminal, trial_handler, "AGENTS.md")
    elif agent_name == AgentName.MACRO:
        _copy_config_file(terminal, trial_handler, "MACRO.md")
