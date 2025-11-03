# ABOUTME: Superpowers plugin enables superpowers skills for Claude Code agent
# ABOUTME: Installs via Claude plugin marketplace in pre-agent phase

from pathlib import Path
from ade_bench.plugins.base_plugin import BasePlugin, PluginContext
from ade_bench.agents.agent_name import AgentName


class SuperpowersPlugin(BasePlugin):
    name = "superpowers"
    description = "Enables superpowers skills for Claude Code agent"

    def should_run(self, phase: str, context: PluginContext) -> bool:
        """Only run for Claude Code agent"""
        return context.agent_name == AgentName.CLAUDE_CODE

    def pre_agent(self, context: PluginContext) -> None:
        """Install superpowers before agent starts"""
        script_path = context.trial_handler.shared_path / "plugins/superpowers/install.sh"

        # Copy script to container at /scripts/ (same location as setup-dbt-mcp.sh)
        context.terminal.copy_to_container(
            script_path,
            Path("/scripts/install-superpowers.sh")
        )

        # Execute installation
        context.terminal.run(
            context.session,
            "bash /scripts/install-superpowers.sh",
            timeout_s=300
        )
