# ABOUTME: dbt-mcp plugin registers dbt MCP server with installed agents
# ABOUTME: Uses existing setup-dbt-mcp.sh script for Snowflake dbt projects

from pathlib import Path
from ade_bench.plugins.base_plugin import BasePlugin, PluginContext


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

        context.terminal.copy_to_container(
            script_path,
            Path("/scripts/setup-dbt-mcp.sh")
        )

        # Convert agent enum to string for script
        agent_name = context.agent_name.value if context.agent_name else "unknown"

        context.terminal.run(
            context.session,
            f"bash /scripts/setup-dbt-mcp.sh {context.db_type} {context.project_type} {agent_name}",
            timeout_s=300
        )
