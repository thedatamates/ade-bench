# ABOUTME: Plugin registry manages plugin instances and executes hooks at lifecycle phases
# ABOUTME: Loads plugins from AVAILABLE_PLUGINS list based on enabled names from CLI

from typing import List
from ade_bench.plugins.base_plugin import BasePlugin, PluginContext
from ade_bench.plugins.superpowers import SuperpowersPlugin


# Static list of available plugins
AVAILABLE_PLUGINS: List[type[BasePlugin]] = [
    SuperpowersPlugin,
]


class PluginRegistry:
    """Registry that loads and executes plugins at lifecycle phases"""

    def __init__(self, enabled_plugin_names: List[str]):
        """Initialize registry with enabled plugins

        Args:
            enabled_plugin_names: List of plugin names to enable (from CLI --plugins)
        """
        self.plugins: List[BasePlugin] = []

        for plugin_class in AVAILABLE_PLUGINS:
            plugin = plugin_class()
            if plugin.name in enabled_plugin_names:
                self.plugins.append(plugin)

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
