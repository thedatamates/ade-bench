"""
Base setup functions for copying files and running scripts.
"""

from pathlib import Path
from typing import Dict, Any
from ..utils.logger import logger


def setup_base_files(terminal, session, task_id: str, variant: Dict[str, Any]) -> None:
    """Setup base files - copy setup files and run scripts."""
    # Strip task key from task id to get task path
    # task_slug = task_id.split(".")[0]
    task_path = Path(__file__).parent.parent.parent / "tasks" / task_id
    setup_script_path = task_path / "setup.sh"
    setup_dir_path = task_path / "setup"

    # Copy setup files
    if setup_script_path.exists():
        # logger.info(f"Found script for task {task_id}!")
        session.copy_to_container(setup_script_path, container_dir="/app", container_filename="setup.sh")
        # logger.info(f"Setup script for task {task_id} was copied!")

    if setup_dir_path.exists():
        terminal.copy_to_container(paths=setup_dir_path, container_dir="/app/setup")

    # Run setup script and remove it
    if setup_script_path.exists():
        # logger.info(f"Gonna run setup script for task {task_id}!")
        session.send_keys(["bash /app/setup.sh", "Enter"], block=True)
        # logger.info(f"Setup script for task {task_id} was run!")
        session.container.exec_run(["rm", "/app/setup.sh"])
        # logger.info(f"Setup script for task {task_id} was removed!")
        session.container.exec_run(["rm", "-rf", "/app/setup"])
        # logger.info(f"Setup directory for task {task_id} was removed!")