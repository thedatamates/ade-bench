"""Oracle agent that uses provided solutions."""

import asyncio
from pathlib import Path
from typing import Any

from docker.models.containers import Container

from ade_bench.agents.base_agent import AgentResult, BaseAgent
from ade_bench.terminal.tmux_session import TmuxSession
from ade_bench.utils.logger import logger


class OracleAgent(BaseAgent):
    """Oracle agent that executes pre-written solutions."""
    
    async def run(
        self,
        task: Any,
        container: Container,
        tmux_session: TmuxSession,
    ) -> AgentResult:
        """Run the oracle solution for a task.
        
        Args:
            task: Task object with metadata
            container: Docker container for execution
            tmux_session: Tmux session for interaction
            
        Returns:
            AgentResult with execution details
        """
        logger.info(f"Running oracle agent for task {self.task_id}")
        
        # Look for solution file
        solution_path = task.path / "solution.sh"
        
        if not solution_path.exists():
            return AgentResult(
                task_id=self.task_id,
                success=False,
                error="No solution.sh file found",
            )
        
        try:
            # Read solution commands
            solution_content = solution_path.read_text().strip()
            
            # Split into individual commands
            commands = [
                cmd.strip()
                for cmd in solution_content.split("\n")
                if cmd.strip() and not cmd.strip().startswith("#")
            ]
            
            # Execute each command
            for i, command in enumerate(commands):
                logger.debug(f"Executing command {i+1}/{len(commands)}: {command}")
                
                try:
                    output = self._execute_command(command, tmux_session)
                    logger.debug(f"Command output: {output[:200]}...")
                    
                    # Wait a bit between commands
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Command failed: {e}")
                    return AgentResult(
                        task_id=self.task_id,
                        success=False,
                        commands_executed=i,
                        error=f"Command {i+1} failed: {str(e)}",
                    )
            
            return AgentResult(
                task_id=self.task_id,
                success=True,
                commands_executed=len(commands),
            )
            
        except Exception as e:
            logger.error(f"Oracle agent failed: {e}")
            return AgentResult(
                task_id=self.task_id,
                success=False,
                error=str(e),
            )