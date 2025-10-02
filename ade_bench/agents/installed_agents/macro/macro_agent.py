import os
import io
import shlex
import tarfile
from pathlib import Path
from typing import Any

from ade_bench.agents.agent_name import AgentName
from ade_bench.agents.installed_agents.abstract_installed_agent import (
    AbstractInstalledAgent,
)
# from ade_bench.agents.base_agent import AgentResult, BaseAgent
from ade_bench.utils.logger import logger
from ade_bench.terminal.tmux_session import TmuxSession
from ade_bench.harness_models import TerminalCommand
from ade_bench.parsers.parser_factory import ParserFactory, ParserName
from ade_bench.config import config

class MacroAgent(AbstractInstalledAgent):
    NAME = AgentName.MACRO
    LOG_FILENAME = "logs.jsonl"
    LOG_DIR = "/var/log/macro-agent"

    def __init__(self, additional_args: str = "", **kwargs):
        super().__init__(**kwargs)
        self.additional_args = additional_args


    @property
    def _env(self) -> dict[str, str]:
        return {
            "MACRO_PLATFORM_API_KEY": os.environ["MACRO_API_KEY"],
        }

    @property
    def _install_agent_script(self) -> Path:
        # Check if we should use custom binary
        if os.environ.get("MACRO_BINARY_PATH"):
            return Path(__file__).parent / "macro-setup-local.sh"
        return Path(__file__).parent / "macro-setup.sh"

    def _create_env_setup_file(self) -> str:
        return "\n".join(
            [f"export {key}='{value}'" for key, value in self._env.items()]
        )

    def _copy_log_file_from_container(self, session: TmuxSession, logging_dir: Path) -> None:
        """Copy the log file from the container to the logging directory."""
        try:
            # Get the working directory from the container
            result = session.container.exec_run(["pwd"])
            if result.exit_code != 0:
                logger.warning("Failed to get working directory from container")
                return

            log_file_path = f"{self.LOG_DIR}/{self.LOG_FILENAME}"

            # Check if the log file exists
            result = session.container.exec_run(["test", "-f", log_file_path])
            if result.exit_code != 0:
                logger.warning(f"Log file {log_file_path} not found in container")
                return

            # Get the file from the container as a tar archive
            archive_data, _ = session.container.get_archive(log_file_path)

            # Extract the file contents from the tar archive
            archive_stream = io.BytesIO(b"".join(archive_data))
            with tarfile.open(fileobj=archive_stream, mode="r") as tar:
                # Get the file from the tar archive
                member = tar.getmember(self.LOG_FILENAME)
                extracted_file = tar.extractfile(member)
                if extracted_file is None:
                    logger.warning("Failed to extract log file from tar archive")
                    return
                file_content = extracted_file.read()

            # Write to the logging directory
            output_file_path = logging_dir / self.LOG_FILENAME
            with open(output_file_path, "wb") as f:
                f.write(file_content)

            logger.info(f"Successfully copied log file to {output_file_path}")

        except Exception as e:
            # Log the error but don't fail the entire task
            logger.warning(f"Failed to copy log file from container: {e}")

    def _run_agent_commands(self, task_prompt: str) -> list[TerminalCommand]:
        escaped_prompt = shlex.quote(task_prompt)
        base_command = f"macro -p {escaped_prompt} -e {self.LOG_DIR}/{self.LOG_FILENAME} --output-format=json"

        if self.additional_args:
            logger.info(f"Running macro with additional args: {self.additional_args}")
            command = f"{base_command} {self.additional_args}"
        else:
            command = base_command

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
        """Parse Macro agent output to extract metrics."""
        # The output should now be cleaner since we're using capture_entire=False
        # But let's still try to extract just the JSON part if there's any extra content
        parser = ParserFactory.get_parser(ParserName.MACRO, task_name=task_name or "macro")
        return parser.parse(pane_output)

#    def perform_task(
#        self,
#        task_prompt: str,
#        session: TmuxSession,
#        logging_dir: Path | None = None,
#        task_name: str | None = None,
#    ) -> AgentResult:
#        session.copy_to_container(
#            self._install_agent_script,
#            container_dir="/installed-agent",
#            container_filename="install-agent.sh",
#        )
#
#        # Copy custom macro binary if specified
#        macro_binary_path = os.environ.get("MACRO_BINARY_PATH")
#
#        if macro_binary_path:
#            binary_path = Path(macro_binary_path)
#            if not binary_path.exists():
#                error_msg = f"MACRO_BINARY_PATH is set but file does not exist: {macro_binary_path}"
#                logger.error(error_msg)
#                raise FileNotFoundError(error_msg)
#
#            logger.info(f"Using custom macro binary from {macro_binary_path}")
#            session.copy_to_container(
#                binary_path,
#                container_dir="/installed-agent",
#                container_filename="macro",
#            )
#
#        # Create logs directory
#        session.container.exec_run(["mkdir", "-p", self.LOG_DIR])
#
#        # Execute outside the session to avoid exposing the env variables.
#        env_setup_content = self._create_env_setup_file()
#        session.container.exec_run(
#            [
#                "sh",
#                "-c",
#                (
#                    f"echo {shlex.quote(env_setup_content)} > "
#                    "/installed-agent/setup-env.sh"
#                ),
#            ]
#        )
#
#        session.send_keys(
#            [
#                "source /installed-agent/setup-env.sh",
#                "Enter",
#            ],
#            block=True,
#            max_timeout_sec=config.setup_timeout_sec,  # Use setup timeout for env setup
#        )
#
#        session.send_keys(
#            [
#                "source /installed-agent/install-agent.sh",
#                "Enter",
#            ],
#            block=True,
#            max_timeout_sec=config.setup_timeout_sec,  # Use setup timeout for installation
#        )
#
#        run_agent_commands = self._run_agent_commands(task_prompt)
#        for command in run_agent_commands:
#            session.send_command(command)
#
#        # Capture the output from the session to extract metrics
#        pane_output = session.capture_pane(capture_entire=True)
#
#        # Parse the output to extract metrics using MacroParser
#        parser = ParserFactory.get_parser(ParserName.MACRO, task_name=task_name or "macro")
#        metrics = parser.parse(pane_output)
#
#        logger.info(f"Extracted metrics from Macro output: {metrics}")
#
#        if logging_dir is not None:
#            self._copy_log_file_from_container(session, logging_dir)
#
#        return AgentResult(
#            input_tokens=metrics["input_tokens"],
#            output_tokens=metrics["output_tokens"],
#            cache_tokens=metrics["cache_tokens"],
#            num_turns=metrics["num_turns"],
#            cost_usd=metrics["cost_usd"],
#            runtime_ms=metrics["runtime_ms"],
#        )
#
