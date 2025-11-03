# ABOUTME: Base plugin interface and context for ADE-Bench plugin system
# ABOUTME: Plugins hook into setup/agent lifecycle phases with conditional execution

from abc import ABC
from dataclasses import dataclass
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ade_bench.terminal.docker_compose_manager import DockerComposeManager
    from ade_bench.handlers.trial_handler import TrialHandler


@dataclass
class PluginContext:
    """Immutable context passed to plugin hooks"""
    terminal: "DockerComposeManager"
    session: Any  # libtmux Session
    trial_handler: "TrialHandler"
    task_id: str
    variant: dict
    agent_name: Optional[str] = None
    db_type: Optional[str] = None
    project_type: Optional[str] = None


class BasePlugin(ABC):
    """Base class for ADE-Bench plugins

    Subclasses override class attributes (name, description) and implement
    lifecycle hook methods (pre_setup, post_setup, pre_agent, post_trial).
    """

    # Subclasses override these
    name: str = ""
    description: str = ""

    def __init__(self):
        pass

    def should_run(self, phase: str, context: PluginContext) -> bool:
        """Override to conditionally execute based on context

        Args:
            phase: Hook phase name (pre_setup, post_setup, pre_agent, post_trial)
            context: Plugin execution context

        Returns:
            True if plugin should run for this phase/context
        """
        return True

    def pre_setup(self, context: PluginContext) -> None:
        """Hook before task's setup.sh execution"""
        pass

    def post_setup(self, context: PluginContext) -> None:
        """Hook after task's setup.sh execution"""
        pass

    def pre_agent(self, context: PluginContext) -> None:
        """Hook before agent execution"""
        pass

    def post_trial(self, context: PluginContext) -> None:
        """Hook after trial completion"""
        pass
