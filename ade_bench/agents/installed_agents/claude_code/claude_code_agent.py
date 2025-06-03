"""Claude Code agent for ADE-Bench."""

import os
import shlex
from pathlib import Path
from typing import Dict

from ade_bench.agents.installed_agents.abstract_installed_agent import (
    AbstractInstalledAgent,
)


class ClaudeCodeAgent(AbstractInstalledAgent):
    """
    Claude Code agent that uses the official Claude Code CLI tool.
    
    This agent is installed inside the container and can interact with
    dbt projects and SQL databases directly.
    """
    
    # Tools available for dbt/SQL tasks
    ALLOWED_TOOLS = ["Bash", "Edit", "Write", "WebFetch"]
    
    def __init__(self, task_id: str, max_episodes: int = 50, **kwargs):
        """
        Initialize Claude Code agent.
        
        Args:
            task_id: ID of the task being run
            max_episodes: Maximum number of interactions
            **kwargs: Additional arguments (including model_name)
        """
        # Get model name from kwargs or use default
        model_name = kwargs.get("model_name", "claude-3-5-sonnet-20241022")
        
        # Initialize both parent classes
        super().__init__(name="claude-code", model_name=model_name)
        
        # Store ADE-Bench specific attributes
        self.task_id = task_id
        self.max_episodes = max_episodes
        self.kwargs = kwargs
        self._model_name = model_name
    
    @property
    def _env(self) -> Dict[str, str]:
        """Environment variables for Claude Code."""
        env_vars = {}
        
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        env_vars["ANTHROPIC_API_KEY"] = api_key
        
        # Set the model if specified
        if self._model_name:
            env_vars["ANTHROPIC_MODEL"] = self._model_name
        
        return env_vars
    
    @property
    def _install_agent_script(self) -> Path:
        """Path to the Claude Code installation script."""
        return Path(__file__).parent / "claude-code-setup.sh"
    
    def _run_agent_command(self, task_description: str) -> str:
        """
        Generate the command to run Claude Code with the task.
        
        Args:
            task_description: The task description to pass to Claude Code
            
        Returns:
            Shell command to execute Claude Code
        """
        # Escape the task description for shell
        escaped_description = shlex.quote(task_description)
        
        # Build the claude command with allowed tools
        tools_arg = " ".join(self.ALLOWED_TOOLS)
        
        # Claude Code CLI command
        # -p: prompt/task description
        # --allowedTools: tools the agent can use
        command = f"claude -p {escaped_description} --allowedTools {tools_arg}"
        
        return command