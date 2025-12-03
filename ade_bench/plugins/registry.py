# ABOUTME: Plugin registry manages plugin instances and executes hooks at lifecycle phases
# ABOUTME: Loads plugins from AVAILABLE_PLUGINS list based on enabled names from CLI

from typing import List, Set
from ade_bench.plugins.base_plugin import BasePlugin, PluginContext
from ade_bench.plugins.superpowers import SuperpowersPlugin
from ade_bench.plugins.dbt_mcp import DbtMcpPlugin


# Static list of available plugins
AVAILABLE_PLUGINS: List[type[BasePlugin]] = [
    SuperpowersPlugin,
    DbtMcpPlugin,
]


class PluginRegistry:
    """Registry that loads and executes plugins at lifecycle phases"""

    def __init__(self, enabled_plugin_names: List[str]):
        """Initialize registry with enabled plugins

        Args:
            enabled_plugin_names: List of plugin names to enable (from CLI --plugins)

        Raises:
            ValueError: If any requested plugin name is not found in AVAILABLE_PLUGINS
        """
        self.plugins: List[BasePlugin] = []
        self.plugins_run: Set[str] = set()  # Track which plugins actually ran

        # Build map of available plugin names
        available_plugin_map = {}
        for plugin_class in AVAILABLE_PLUGINS:
            plugin = plugin_class()
            available_plugin_map[plugin.name] = plugin_class

        # Validate all requested plugins exist
        available_names = set(available_plugin_map.keys())
        requested_names = set(enabled_plugin_names)
        unknown_plugins = requested_names - available_names

        if unknown_plugins:
            raise ValueError(
                f"Unknown plugin(s): {', '.join(sorted(unknown_plugins))}. "
                f"Available plugins: {', '.join(sorted(available_names))}"
            )

        # Load requested plugins
        for plugin_name in enabled_plugin_names:
            plugin_class = available_plugin_map[plugin_name]
            self.plugins.append(plugin_class())

    def run_hooks(self, phase: str, context: PluginContext) -> None:
        """Execute all enabled plugins for given phase

        Args:
            phase: Hook phase name (pre_setup, post_setup, pre_agent, post_trial)
            context: Plugin execution context
        """
        for plugin in self.plugins:
            if plugin.should_run(phase, context):
                hook_method = getattr(plugin, phase)
                hook_method(context)
                # Track that this plugin actually ran
                self.plugins_run.add(plugin.name)

    def did_plugin_run(self, plugin_name: str) -> bool:
        """Check if a specific plugin ran during this trial

        Args:
            plugin_name: Name of the plugin to check

        Returns:
            True if the plugin ran, False otherwise
        """
        return plugin_name in self.plugins_run
