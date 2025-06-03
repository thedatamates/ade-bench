"""Factory for creating agents."""

from typing import Any, Dict, Optional

from ade_bench.agents.base_agent import BaseAgent
from ade_bench.agents.oracle_agent import OracleAgent
from ade_bench.agents.installed_agents.claude_code import ClaudeCodeAgent


class AgentFactory:
    """Factory for creating agent instances."""
    
    _agent_registry = {
        "oracle": OracleAgent,
        "claude-code": ClaudeCodeAgent,
    }
    
    @classmethod
    def create_agent(
        cls,
        agent_name: str,
        task_id: str,
        model_name: Optional[str] = None,
        max_episodes: int = 50,
        **kwargs,
    ) -> BaseAgent:
        """Create an agent instance.
        
        Args:
            agent_name: Name of the agent type
            task_id: ID of the task
            model_name: Model name for LLM agents
            max_episodes: Maximum interactions
            **kwargs: Additional agent arguments
            
        Returns:
            Initialized agent instance
        """
        if agent_name not in cls._agent_registry:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent_class = cls._agent_registry[agent_name]
        
        # Add model_name to kwargs if provided
        if model_name:
            kwargs["model_name"] = model_name
        
        return agent_class(
            task_id=task_id,
            max_episodes=max_episodes,
            **kwargs,
        )
    
    @classmethod
    def register_agent(cls, name: str, agent_class: type[BaseAgent]) -> None:
        """Register a new agent type.
        
        Args:
            name: Name to register the agent under
            agent_class: Agent class to register
        """
        cls._agent_registry[name] = agent_class