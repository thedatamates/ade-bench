"""Base agent class for ADE-Bench."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from docker.models.containers import Container
from pydantic import BaseModel, Field

from ade_bench.terminal.tmux_session import TmuxSession


class AgentResult(BaseModel):
    """Result from an agent's execution."""
    
    task_id: str
    success: bool
    commands_executed: int = 0
    token_usage: Dict[str, int] = Field(default_factory=dict)
    error: Optional[str] = None
    markers: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(
        self,
        task_id: str,
        max_episodes: int = 50,
        **kwargs,
    ):
        """Initialize base agent.
        
        Args:
            task_id: ID of the task being run
            max_episodes: Maximum number of interactions
            **kwargs: Additional agent-specific arguments
        """
        self.task_id = task_id
        self.max_episodes = max_episodes
        self.kwargs = kwargs
    
    @abstractmethod
    async def run(
        self,
        task: Any,
        container: Container,
        tmux_session: TmuxSession,
    ) -> AgentResult:
        """Run the agent on a task.
        
        Args:
            task: Task object with metadata
            container: Docker container for execution
            tmux_session: Tmux session for interaction
            
        Returns:
            AgentResult with execution details
        """
        pass
    
    def _execute_command(
        self,
        command: str,
        tmux_session: TmuxSession,
    ) -> str:
        """Execute a command in the tmux session.
        
        Args:
            command: Command to execute
            tmux_session: Tmux session
            
        Returns:
            Output from the command
        """
        exit_code, output = tmux_session.send_command(command)
        
        if exit_code != 0:
            raise RuntimeError(f"Command failed: {command}")
        
        # Get the current pane content for feedback
        return tmux_session.capture_pane()