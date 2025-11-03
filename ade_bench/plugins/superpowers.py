# ABOUTME: Superpowers plugin enables superpowers skills for Claude Code agent
# ABOUTME: Installs via Claude plugin marketplace in pre-agent phase

import logging
from pathlib import Path
from ade_bench.plugins.base_plugin import BasePlugin, PluginContext
from ade_bench.agents.agent_name import AgentName

logger = logging.getLogger(__name__)


class SuperpowersPlugin(BasePlugin):
    name = "superpowers"
    description = "Enables superpowers skills for Claude Code agent"

    def should_run(self, phase: str, context: PluginContext) -> bool:
        """Only run for Claude Code agent"""
        return context.agent_name == AgentName.CLAUDE_CODE

    def pre_agent(self, context: PluginContext) -> None:
        """Install superpowers before agent starts"""
        script_path = context.trial_handler._shared_path / "plugins/superpowers/install.sh"

        logger.info(f"[SuperpowersPlugin] Preparing to install superpowers")
        logger.info(f"[SuperpowersPlugin] Source script path: {script_path}")
        logger.info(f"[SuperpowersPlugin] Script exists: {script_path.exists()}")

        if not script_path.exists():
            logger.error(f"[SuperpowersPlugin] Script not found at {script_path}")
            raise FileNotFoundError(f"Superpowers install script not found at {script_path}")

        # Copy script to container at /scripts/
        logger.info(f"[SuperpowersPlugin] Copying script to container at /scripts/install-superpowers.sh")
        context.terminal.copy_to_container(
            paths=script_path,
            container_dir="/scripts",
            container_filename="install-superpowers.sh"
        )
        logger.info(f"[SuperpowersPlugin] Script copied successfully")

        # Execute installation
        logger.info(f"[SuperpowersPlugin] Executing installation script")
        context.terminal.run(
            context.session,
            "bash /scripts/install-superpowers.sh",
            timeout_s=300
        )
        logger.info(f"[SuperpowersPlugin] Superpowers installation completed")

