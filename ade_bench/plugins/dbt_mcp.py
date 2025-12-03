# ABOUTME: dbt-mcp plugin registers dbt MCP server with installed agents
# ABOUTME: Uses existing setup-dbt-mcp.sh script for Snowflake dbt projects

import logging
from pathlib import Path
from ade_bench.plugins.base_plugin import BasePlugin, PluginContext

logger = logging.getLogger(__name__)


class DbtMcpPlugin(BasePlugin):
    name = "dbt-mcp"
    description = "Registers dbt MCP server with installed agents"

    def should_run(self, phase: str, context: PluginContext) -> bool:
        """Only run for dbt projects on Snowflake"""
        is_dbt = context.project_type in ["dbt", "dbt-fusion"]
        is_snowflake = context.db_type == "snowflake"
        return is_dbt and is_snowflake

    def pre_agent(self, context: PluginContext) -> None:
        """Register dbt MCP server before agent starts"""
        # Use existing script at shared/scripts/setup-dbt-mcp.sh
        script_path = context.trial_handler._shared_path / "scripts/setup-dbt-mcp.sh"

        logger.info(f"[DbtMcpPlugin] Preparing to register dbt MCP server")
        logger.info(f"[DbtMcpPlugin] Source script path: {script_path}")
        logger.info(f"[DbtMcpPlugin] Script exists: {script_path.exists()}")

        if not script_path.exists():
            logger.error(f"[DbtMcpPlugin] Script not found at {script_path}")
            raise FileNotFoundError(f"dbt-mcp setup script not found at {script_path}")

        logger.info(f"[DbtMcpPlugin] Copying script to container at /scripts/setup-dbt-mcp.sh")
        context.terminal.copy_to_container(
            paths=script_path,
            container_dir="/scripts",
            container_filename="setup-dbt-mcp.sh"
        )
        logger.info(f"[DbtMcpPlugin] Script copied successfully")

        # Convert agent enum to string for script
        agent_name = context.agent_name.value if context.agent_name else "unknown"

        logger.info(f"[DbtMcpPlugin] Executing dbt-mcp setup for {agent_name}")
        context.session.send_keys(
            [
                f"bash /scripts/setup-dbt-mcp.sh {context.db_type} {context.project_type} {agent_name}",
                "Enter",
            ],
            block=True,
            max_timeout_sec=300
        )
        logger.info(f"[DbtMcpPlugin] dbt-mcp setup completed")
