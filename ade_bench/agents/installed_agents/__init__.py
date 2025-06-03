"""Installed agents that run inside Docker containers."""

from .abstract_installed_agent import AbstractInstalledAgent
from .claude_code import ClaudeCodeAgent

__all__ = ["AbstractInstalledAgent", "ClaudeCodeAgent"]