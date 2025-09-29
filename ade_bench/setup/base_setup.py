"""
Base setup functions for copying files and running scripts.
"""

from pathlib import Path
from typing import Dict, Any
from ..utils.logger import logger
from ..terminal.docker_compose_manager import DockerComposeManager


def setup_base_files(terminal, session, task_id: str, variant: Dict[str, Any], trial_handler) -> None:
    """Setup base files - copy setup files and run scripts."""
    setup_script_path = trial_handler.task_setup_script_path
    setup_dir_path = trial_handler.task_setup_dir_path

    # Copy setup files
    if setup_script_path.exists():
        terminal.copy_to_container(
            paths=setup_script_path,
            container_dir=str(DockerComposeManager.CONTAINER_APP_DIR),
            container_filename="setup.sh"
        )

    if setup_dir_path.exists():
        terminal.copy_to_container(
            paths=setup_dir_path,
            container_dir=str(DockerComposeManager.CONTAINER_SETUP_DIR)
        )

    # Run setup script and remove it
    if setup_script_path.exists():
        # Build command with optional parameters
        command = f"bash {DockerComposeManager.CONTAINER_APP_DIR}/setup.sh"
        db_type = variant.get("db_type")
        project_type = variant.get("project_type")
        if db_type:
            command += f" --db-type={db_type}"
        if project_type:
            command += f" --project-type={project_type}"

        session.send_keys([command, "Enter"], block=True)
        session.container.exec_run(["rm", f"{DockerComposeManager.CONTAINER_APP_DIR}/setup.sh"])
        session.container.exec_run(["rm", "-rf", str(DockerComposeManager.CONTAINER_SETUP_DIR)])