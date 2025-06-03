"""Tmux session management for ADE-Bench."""

import re
import time
from pathlib import Path
from typing import List, Optional, Tuple, Union

import docker
from docker.models.containers import Container

from ade_bench.terminal.docker_compose_manager import DockerComposeManager
from ade_bench.utils.logger import logger


class TmuxSession:
    """Manages tmux sessions within Docker containers."""
    
    _ENTER_KEYS = {"Enter", "C-m", "KPEnter", "C-j", "^M", "^J"}
    _ENDS_WITH_NEWLINE_PATTERN = r"[\r\n]$"
    _NEWLINE_CHARS = "\r\n"
    _TMUX_COMPLETION_COMMAND = "; tmux wait -S done"

    def __init__(
        self,
        session_name: str,
        container: Container,
        working_dir: Optional[str] = None,
        log_file_path: Optional[Path] = None,
    ):
        """Initialize tmux session.
        
        Args:
            session_name: Name for the tmux session
            container: Docker container to run tmux in
            working_dir: Working directory in container
            log_file_path: Path to save session logs
        """
        self.container = container
        self._session_name = session_name
        self._working_dir = working_dir or "/dbt_project"
        self._log_file_path = log_file_path
        self._logger = logger.getChild(__name__)

        # Verify tmux is installed
        result = self.container.exec_run(["tmux", "-V"])
        if result.exit_code != 0:
            raise RuntimeError(
                "tmux is not installed in the container. "
                "Please install tmux in the container to run ADE-Bench."
            )

    @classmethod
    def from_container_name(
        cls, session_name: str, container_name: str, **kwargs
    ) -> "TmuxSession":
        """Create TmuxSession from container name."""
        client = docker.from_env()
        container = client.containers.get(container_name)
        return cls(session_name=session_name, container=container, **kwargs)

    @property
    def logging_path(self) -> Path:
        """Path to session log file in container."""
        return Path(DockerComposeManager.CONTAINER_LOGS_PATH) / f"{self._session_name}.log"

    @property
    def _tmux_start_session(self) -> List[str]:
        """Command to start tmux session."""
        return [
            "bash",
            "-c",
            (
                f"cd {self._working_dir} && "
                f"tmux new-session -x 160 -y 40 -d -s {self._session_name} \\; "
                f"pipe-pane -t {self._session_name} "
                f'"cat > {self.logging_path}"'
            ),
        ]

    def _tmux_send_keys(self, keys: List[str]) -> List[str]:
        """Command to send keys to tmux session."""
        return [
            "tmux",
            "send-keys",
            "-t",
            self._session_name,
            *keys,
        ]

    def _tmux_capture_pane(self, capture_entire: bool = False) -> List[str]:
        """Command to capture tmux pane content."""
        if capture_entire:
            extra_args = ["-S", "-"]
        else:
            extra_args = []

        return [
            "tmux",
            "capture-pane",
            "-p",
            *extra_args,
            "-t",
            self._session_name,
        ]

    def start(self) -> None:
        """Start the tmux session."""
        self._logger.info(f"Starting tmux session: {self._session_name}")
        result = self.container.exec_run(self._tmux_start_session)
        if result.exit_code != 0:
            raise RuntimeError(f"Failed to start tmux session: {result.output.decode()}")
        
        # Give tmux time to initialize
        time.sleep(0.5)
        
        # Clear the screen
        self.send_keys(["clear", "Enter"])

    def stop(self) -> None:
        """Stop the tmux session."""
        self._logger.info(f"Stopping tmux session: {self._session_name}")
        self.container.exec_run([
            "tmux",
            "kill-session",
            "-t",
            self._session_name,
        ])

    def _is_enter_key(self, key: str) -> bool:
        """Check if key is an enter key."""
        return key in self._ENTER_KEYS

    def _ends_with_newline(self, key: str) -> bool:
        """Check if key ends with newline."""
        result = re.search(self._ENDS_WITH_NEWLINE_PATTERN, key)
        return result is not None

    def _is_executing_command(self, key: str) -> bool:
        """Check if key will execute a command."""
        return self._is_enter_key(key) or self._ends_with_newline(key)

    def _prevent_execution(self, keys: List[str]) -> List[str]:
        """Remove execution keys from the end of the list."""
        keys = keys.copy()
        while keys and self._is_executing_command(keys[-1]):
            if self._is_enter_key(keys[-1]):
                keys.pop()
            else:
                stripped_key = keys[-1].rstrip(self._NEWLINE_CHARS)
                if stripped_key:
                    keys[-1] = stripped_key
                else:
                    keys.pop()
        return keys

    def _prepare_keys(
        self,
        keys: Union[str, List[str]],
        block: bool,
    ) -> Tuple[List[str], bool]:
        """
        Prepare keys for sending to the terminal.

        Args:
            keys: The keys to send to the terminal
            block: Whether to wait for the command to complete

        Returns:
            Tuple of (keys to send, whether blocking)
        """
        if isinstance(keys, str):
            keys = [keys]

        if not block or not keys or not self._is_executing_command(keys[-1]):
            return keys, False

        keys = self._prevent_execution(keys)
        keys.extend([self._TMUX_COMPLETION_COMMAND, "Enter"])

        return keys, True

    def _send_blocking_keys(
        self,
        keys: List[str],
        max_timeout_sec: float,
    ) -> None:
        """Send keys and wait for completion."""
        start_time_sec = time.time()
        self.container.exec_run(self._tmux_send_keys(keys))

        result = self.container.exec_run(
            ["timeout", f"{max_timeout_sec}s", "tmux", "wait", "done"]
        )
        if result.exit_code != 0:
            raise TimeoutError(f"Command timed out after {max_timeout_sec} seconds")

        elapsed_time_sec = time.time() - start_time_sec
        self._logger.debug(f"Blocking command completed in {elapsed_time_sec:.2f}s.")

    def _send_non_blocking_keys(
        self,
        keys: List[str],
        min_timeout_sec: float,
    ) -> None:
        """Send keys without waiting."""
        start_time_sec = time.time()
        self.container.exec_run(self._tmux_send_keys(keys))

        elapsed_time_sec = time.time() - start_time_sec

        if elapsed_time_sec < min_timeout_sec:
            time.sleep(min_timeout_sec - elapsed_time_sec)

    def send_keys(
        self,
        keys: Union[str, List[str]],
        block: bool = False,
        min_timeout_sec: float = 0.0,
        max_timeout_sec: float = 180.0,
    ) -> None:
        """
        Send keys to the tmux session.

        Args:
            keys: The keys to send to the tmux session
            block: Whether to wait for the command to complete
            min_timeout_sec: Minimum time to wait after executing
            max_timeout_sec: Maximum time to wait for blocking commands
        """
        if block and min_timeout_sec > 0.0:
            self._logger.debug("min_timeout_sec will be ignored because block is True.")

        prepared_keys, is_blocking = self._prepare_keys(
            keys=keys,
            block=block,
        )

        self._logger.debug(
            f"Sending keys: {prepared_keys}"
            f" min_timeout_sec: {min_timeout_sec}"
            f" max_timeout_sec: {max_timeout_sec}"
        )

        if is_blocking:
            self._send_blocking_keys(
                keys=prepared_keys,
                max_timeout_sec=max_timeout_sec,
            )
        else:
            self._send_non_blocking_keys(
                keys=prepared_keys,
                min_timeout_sec=min_timeout_sec,
            )

    def send_command(self, command: str, block: bool = True, timeout: float = 180.0) -> Tuple[int, str]:
        """Send a command to the tmux session.
        
        This is the simplified interface for ADE-Bench that returns exit code and output.
        
        Args:
            command: Command to send
            block: Whether to wait for completion (default: True)
            timeout: Maximum time to wait in seconds
            
        Returns:
            Tuple of (exit_code, output)
        """
        self._logger.debug(f"Sending command: {command}")
        
        # For long-running commands, capture output differently
        if "install" in command or timeout > 60:
            # Use a different approach for install scripts
            return self._send_long_command(command, timeout)
        
        # Capture initial pane state
        initial_pane = self.capture_pane()
        
        # Send the command
        if not command.endswith("\n"):
            keys = [command, "Enter"]
        else:
            keys = [command]
        
        try:
            self.send_keys(keys, block=block, max_timeout_sec=timeout)
            
            # Give command time to produce output
            time.sleep(0.5)
            
            # Capture final pane state
            final_pane = self.capture_pane()
            
            # Extract new output
            output = self._extract_new_output(initial_pane, final_pane)
            
            # Try to get exit code from the last command
            exit_code = self._get_last_exit_code()
            
            return exit_code, output
            
        except TimeoutError:
            self._logger.error(f"Command timed out: {command}")
            return 1, "Command timed out"
        except Exception as e:
            self._logger.error(f"Error executing command: {e}")
            self._logger.exception("Full traceback:")
            return 1, str(e)

    def _send_long_command(self, command: str, timeout: float) -> Tuple[int, str]:
        """Send a long-running command and capture its output via logging."""
        self._logger.info(f"Sending long-running command: {command}")
        
        # Create a unique log file for this command
        import uuid
        log_id = str(uuid.uuid4())[:8]
        log_file = f"/logs/cmd_{log_id}.log"
        
        # Wrap command to capture output and exit code
        wrapped_command = f"""
{{
    {command}
    echo "EXIT_CODE:$?" >> {log_file}
}} 2>&1 | tee -a {log_file}
"""
        
        # Send the wrapped command
        self.send_keys([wrapped_command, "Enter"], block=True, max_timeout_sec=timeout)
        
        # Give it a moment to finish writing
        time.sleep(1)
        
        # Read the log file
        result = self.container.exec_run(["cat", log_file])
        if result.exit_code != 0:
            self._logger.error(f"Failed to read log file: {log_file}")
            return 1, "Failed to capture command output"
        
        output = result.output.decode()
        
        # Extract exit code from output
        exit_code = 0
        if "EXIT_CODE:" in output:
            lines = output.split('\n')
            for line in reversed(lines):
                if line.startswith("EXIT_CODE:"):
                    try:
                        exit_code = int(line.split(":")[-1])
                    except ValueError:
                        exit_code = 1
                    # Remove the EXIT_CODE line from output
                    output = '\n'.join(l for l in lines if not l.startswith("EXIT_CODE:"))
                    break
        
        self._logger.debug(f"Long command completed with exit code: {exit_code}")
        return exit_code, output

    def _extract_new_output(self, initial: str, final: str) -> str:
        """Extract new output by comparing pane states."""
        initial_lines = initial.strip().split('\n') if initial.strip() else []
        final_lines = final.strip().split('\n') if final.strip() else []
        
        # If no final output, return empty
        if not final_lines:
            return ""
        
        # If no initial output, return all final output
        if not initial_lines:
            return '\n'.join(final_lines)
        
        # Find the first initial line in final output
        start_idx = -1
        for i, final_line in enumerate(final_lines):
            if final_line == initial_lines[0]:
                # Check if rest of initial matches
                match = True
                for j, initial_line in enumerate(initial_lines):
                    if i + j >= len(final_lines) or final_lines[i + j] != initial_line:
                        match = False
                        break
                if match:
                    start_idx = i + len(initial_lines)
                    break
        
        # If we found where initial ends, return everything after
        if start_idx >= 0 and start_idx < len(final_lines):
            return '\n'.join(final_lines[start_idx:])
        
        # If initial content not found in final, assume all final is new
        return '\n'.join(final_lines)

    def _get_last_exit_code(self) -> int:
        """Get the exit code of the last command."""
        # Send command to get exit code
        self.send_keys(["echo $?", "Enter"], block=True, max_timeout_sec=5)
        time.sleep(0.2)
        
        pane = self.capture_pane()
        lines = pane.strip().split('\n')
        
        # Look for exit code in recent lines
        for line in reversed(lines[-5:]):
            line = line.strip()
            if line.isdigit():
                return int(line)
        
        return 0  # Default to success if we can't find it

    def capture_pane(self, capture_entire: bool = False) -> str:
        """Capture the current pane content."""
        try:
            result = self.container.exec_run(
                self._tmux_capture_pane(capture_entire=capture_entire)
            )
            return result.output.decode("utf-8")
        except Exception as e:
            self._logger.error(f"Failed to capture pane: {e}")
            return ""

    def get_log_content(self) -> str:
        """Get the session log content from container."""
        result = self.container.exec_run([
            "cat",
            str(self.logging_path)
        ])
        
        if result.exit_code != 0:
            return ""
        
        return result.output.decode()

    def wait_for_prompt(self, timeout: int = 30) -> bool:
        """Wait for a command prompt to appear.
        
        Args:
            timeout: Maximum seconds to wait
            
        Returns:
            True if prompt found, False if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            pane_content = self.capture_pane()
            
            # Check for common prompt patterns
            if any(pattern in pane_content for pattern in ["$", "#", ">"]):
                # Check if last line looks like a prompt
                lines = pane_content.strip().split("\n")
                if lines and any(p in lines[-1] for p in ["$", "#", ">"]):
                    return True
            
            time.sleep(0.5)
        
        return False
    
    def copy_to_container(
        self,
        paths: Union[List[Path], Path],
        container_dir: Optional[str] = None,
        container_filename: Optional[str] = None,
    ) -> None:
        """Copy files to the container using DockerComposeManager's static method."""
        DockerComposeManager.copy_to_container(
            container=self.container,
            paths=paths,
            container_dir=container_dir,
            container_filename=container_filename,
        )