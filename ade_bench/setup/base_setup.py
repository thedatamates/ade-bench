"""
Base setup functions for copying files and running scripts.
"""

from pathlib import Path
from typing import Dict, Any


def setup_base_files(terminal, session, task_id: str, variant: Dict[str, Any]) -> None:
    """Setup base files - copy setup files and run scripts."""
    task_path = Path(__file__).parent.parent.parent / "tasks" / task_id
    setup_script_path = task_path / "setup.sh"
    setup_dir_path = task_path / "setup"

    # Copy setup files
    if setup_script_path.exists():
        session.copy_to_container(setup_script_path, container_dir="/app", container_filename="setup.sh")

    if setup_dir_path.exists():
        terminal.copy_to_container(paths=setup_dir_path, container_dir="/app/setup")

    # Run setup script and remove it
    if setup_script_path.exists():
        session.send_keys(["bash /app/setup.sh", "Enter"], block=True)
        session.container.exec_run(["rm", "/app/setup.sh"])
        session.container.exec_run(["rm", "-rf", "/app/setup"])