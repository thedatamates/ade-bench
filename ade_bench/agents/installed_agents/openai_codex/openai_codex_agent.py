import os
import shlex
from pathlib import Path
from typing import Any

from ade_bench.agents.agent_name import AgentName
from ade_bench.agents.installed_agents.abstract_installed_agent import (
    AbstractInstalledAgent,
)
from ade_bench.harness_models import TerminalCommand
from ade_bench.parsers.codex_parser import CodexParser
from ade_bench.config import config


class OpenAICodexAgent(AbstractInstalledAgent):
    NAME = AgentName.OPENAI_CODEX
    # Codex doesn't seem to have an allowed tools option, but I didn't fully check.
    # ALLOWED_TOOLS = ["Bash", "Edit", "Write", "NotebookEdit", "WebFetch"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._codex_parser = CodexParser()

    @property
    def _env(self) -> dict[str, str]:
        return {
            "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
        }

    @property
    def _install_agent_script(self) -> os.PathLike:
        return Path(__file__).parent / "openai_codex-setup.sh"

    def _run_agent_commands(self, task_prompt: str) -> list[TerminalCommand]:
        escaped_prompt = shlex.quote(task_prompt)

        key = self._env["OPENAI_API_KEY"]

        return [
            TerminalCommand(
                command=
                f"echo 'AGENT RESPONSE: ' && "
                f"codex login --api-key {key} && "
                f"codex exec --skip-git-repo-check --full-auto {escaped_prompt} ",
                min_timeout_sec=0.0,
                max_timeout_sec=config.default_agent_timeout_sec,
                block=True,
                append_enter=True,
            )
        ]

    def _parse_agent_output(self, output: str) -> dict[str, Any]:
        """Parse Codex agent output to extract metrics."""
        # The output should now be cleaner since we're using capture_entire=False
        # But let's still try to extract just the JSON part if there's any extra content
        return self._codex_parser.parse(output)
