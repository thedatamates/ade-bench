import os
import shlex
from pathlib import Path
from typing import Any

from ade_bench.agents.agent_name import AgentName
from ade_bench.agents.installed_agents.abstract_installed_agent import (
    AbstractInstalledAgent,
)
from ade_bench.harness_models import TerminalCommand
from ade_bench.parsers.gemini_parser import GeminiParser
from ade_bench.config import config


class GeminiCLIAgent(AbstractInstalledAgent):
    NAME = AgentName.GEMINI_CLI
    # Yolo Mode (-y) lets Gemini do whatever it wants.
    # ALLOWED_TOOLS = ["Bash", "Edit", "Write", "NotebookEdit", "WebFetch"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._gemini_parser = GeminiParser()

    @property
    def _env(self) -> dict[str, str]:
        return {
            "GEMINI_API_KEY": os.environ["GEMINI_API_KEY"],
        }

    @property
    def _install_agent_script(self) -> os.PathLike:
        return Path(__file__).parent / "gemini_cli-setup.sh"

    def _run_agent_commands(self, task_prompt: str) -> list[TerminalCommand]:
        header = "echo 'AGENT RESPONSE: ' && "
        escaped_prompt = shlex.quote(task_prompt)
        command = f"{header} gemini --output-format json -y -p {escaped_prompt}"

        if self._model_name:
            command += f" --model {self._model_name}"

        return [
            TerminalCommand(
                command=command,
                min_timeout_sec=0.0,
                max_timeout_sec=config.default_agent_timeout_sec,
                block=True,
                append_enter=True,
            )
        ]

    def _parse_agent_output(self, output: str) -> dict[str, Any]:
        """Parse Gemini agent output to extract metrics."""
        return self._gemini_parser.parse(output)
