from pathlib import Path
import shlex
import os
import tarfile
import io

from ade_bench.agents.agent_name import AgentName
from ade_bench.agents.base_agent import AgentResult, BaseAgent
from ade_bench.terminal.tmux_session import TmuxSession
from ade_bench.utils.logger import logger
from ade_bench.harness_models import TerminalCommand


class MacroAgent(BaseAgent):
    NAME = AgentName.MACRO
    LOG_FILENAME = "logs.jsonl"
    LOG_DIR = "/var/log/macro-agent"


    @property
    def _env(self) -> dict[str, str]:
        return {
            "MACRO_PLATFORM_API_KEY": os.environ["MACRO_API_KEY"],
        }

    @property
    def _install_agent_script(self) -> Path:
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

    def _run_agent_commands(self, task_description: str) -> list[TerminalCommand]:
        escaped_description = shlex.quote(task_description)
        return [
            TerminalCommand(
                command=f"macro -p {escaped_description}",
                min_timeout_sec=0.0,
                max_timeout_sec=float("inf"),
                block=True,
                append_enter=True,
            )
        ]

    def perform_task(
        self,
        task_description: str,
        session: TmuxSession,
        logging_dir: Path | None = None,
        task_name: str | None = None,
    ) -> AgentResult:
        session.copy_to_container(
            self._install_agent_script,
            container_dir="/installed-agent",
            container_filename="install-agent.sh",
        )

        session.container.__format__

        # Execute outside the session to avoid exposing the env variables.
        env_setup_content = self._create_env_setup_file()
        session.container.exec_run(
            [
                "sh",
                "-c",
                (
                    f"echo {shlex.quote(env_setup_content)} > "
                    "/installed-agent/setup-env.sh"
                ),
            ]
        )

        session.send_keys(
            [
                "source /installed-agent/setup-env.sh",
                "Enter",
            ],
            block=True,
            max_timeout_sec=float("inf"),
        )

        session.send_keys(
            [
                "source /installed-agent/install-agent.sh",
                "Enter",
            ],
            block=True,
            max_timeout_sec=float("inf"),
        )

        run_agent_commands = self._run_agent_commands(task_description)
        for command in run_agent_commands:
            session.send_command(command)

        if logging_dir is not None:
            self._copy_log_file_from_container(session, logging_dir)

        return AgentResult(
            total_input_tokens=0,
            total_output_tokens=0,
        )
