"""
Any agent that implements this abstract class will be installed into the task container
and executed using a shell command.

This is useful for agents that are not compatible with the tools we provide to interact
with the task container externally.

Adapted from terminal-bench for ADE-Bench's dbt/SQL focused tasks.
"""

import shlex
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ade_bench.agents.base_agent import BaseAgent, AgentResult
from ade_bench.terminal.tmux_session import TmuxSession
from ade_bench.utils.logger import logger
from docker.models.containers import Container


class AbstractInstalledAgent(BaseAgent, ABC):
    """Base class for agents that need to be installed inside the container."""
    
    def __init__(self, name: str, model_name: str):
        # Don't call BaseAgent.__init__ here - it will be called by the concrete agent
        self.name = name
        self.model_name = model_name
        self._logger = logger.getChild(f"installed_agent.{name}")
    
    @property
    @abstractmethod
    def _env(self) -> Dict[str, str]:
        """
        Environment variables to use when running the agent (e.g. ANTHROPIC_API_KEY).
        """
        ...
    
    @property
    @abstractmethod
    def _install_agent_script(self) -> Path:
        """
        Script to install the agent in the container.
        """
        ...
    
    @abstractmethod
    def _run_agent_command(self, task_description: str) -> str:
        """
        Command to run the agent with the given task description.
        """
        pass
    
    def _create_env_setup_file(self) -> str:
        """Create shell script content to set environment variables."""
        return "\n".join(
            [f"export {key}='{value}'" for key, value in self._env.items()]
        )
    
    async def run(
        self,
        task: Any,
        container: Container,
        tmux_session: TmuxSession,
    ) -> AgentResult:
        """
        Run the agent on the given task.
        
        Args:
            task: Task object with metadata
            container: Docker container for execution
            tmux_session: Tmux session to interact with
            
        Returns:
            AgentResult with success status
        """
        # Get task description from task object
        timeout_seconds = getattr(task, 'timeout_seconds', 1800)
        try:
            # Copy install script to container
            self._logger.info("Installing agent in container...")
            tmux_session.copy_to_container(
                self._install_agent_script,
                container_dir="/installed-agent",
                container_filename="install-agent.sh",
            )
            
            # Create environment setup file
            env_setup_content = self._create_env_setup_file()
            tmux_session.container.exec_run(
                [
                    "sh",
                    "-c",
                    (
                        f"echo {shlex.quote(env_setup_content)} > "
                        "/installed-agent/setup-env.sh"
                    ),
                ]
            )
            
            # Source environment variables
            exit_code, output = tmux_session.send_command(
                "source /installed-agent/setup-env.sh"
            )
            if exit_code != 0:
                self._logger.error(f"Failed to set up environment: {output}")
                return AgentResult(
                    task_id=task.task_id,
                    success=False,
                    error=f"Environment setup failed: {output}"
                )
            
            # Install the agent
            self._logger.info("Running agent installation script...")
            
            # Run the install script and capture output to a log file
            install_command = (
                "source /installed-agent/install-agent.sh 2>&1 | "
                "tee /logs/agent_install.log"
            )
            
            exit_code, output = tmux_session.send_command(
                install_command,
                timeout=600  # 10 minutes for installation
            )
            
            # Also try to get the install log content
            log_result = tmux_session.container.exec_run(
                ["cat", "/logs/agent_install.log"]
            )
            if log_result.exit_code == 0:
                install_log = log_result.output.decode()
                self._logger.info(f"Install script output:\n{install_log}")
            
            if exit_code != 0:
                self._logger.error(f"Failed to install agent with exit code {exit_code}")
                self._logger.error(f"Output: {output}")
                return AgentResult(
                    task_id=task.task_id,
                    success=False,
                    error=f"Agent installation failed with exit code {exit_code}"
                )
            
            # Run the agent with the task
            self._logger.info("Running agent on task...")
            agent_command = self._run_agent_command(task.description)
            
            # Log the exact command being run
            self._logger.info(f"Running agent command: {agent_command}")
            
            # For ADE-Bench, we want the agent to complete the dbt/SQL task
            # Run with longer timeout since agent tasks can take time
            exit_code, output = tmux_session.send_command(
                agent_command,
                timeout=timeout_seconds
            )
            
            # Log the agent output
            self._logger.info(f"Agent output:\n{output}")
            
            # Check if the agent completed successfully
            success = exit_code == 0
            
            if not success:
                self._logger.error(f"Agent failed with exit code {exit_code}")
                self._logger.error(f"Agent error output: {output}")
                return AgentResult(
                    task_id=task.task_id,
                    success=False,
                    error=f"Agent exited with code {exit_code}"
                )
            
            self._logger.info("Agent completed successfully")
            
            # Also log the tmux session content for debugging
            try:
                session_log = tmux_session.get_log_content()
                if session_log:
                    log_path = f"/logs/session_{task.task_id}.log"
                    tmux_session.container.exec_run(
                        ["sh", "-c", f"echo {shlex.quote(session_log)} > {log_path}"]
                    )
                    self._logger.debug(f"Session log saved to {log_path}")
            except Exception as e:
                self._logger.warning(f"Failed to save session log: {e}")
            
            return AgentResult(
                task_id=task.task_id,
                success=True,
                commands_executed=1,  # We executed the main agent command
                error=None
            )
            
        except Exception as e:
            self._logger.error(f"Error running installed agent: {e}")
            return AgentResult(
                task_id=task.task_id,
                success=False,
                error=str(e)
            )