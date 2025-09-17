"""
DuckDB setup functions.
"""

from typing import Dict, Any
from ..terminal.docker_compose_manager import DockerComposeManager


def setup_duckdb(terminal, session, variant: Dict[str, Any], trial_handler) -> None:
    """Setup DuckDB by copying the database file."""
    db_name = variant.get('db_name')
    if not db_name:
        return

    shared_db_path = trial_handler.get_duckdb_file_path(db_name)

    if shared_db_path.exists():
        terminal.copy_to_container(
            paths=shared_db_path,
            container_dir=str(DockerComposeManager.CONTAINER_APP_DIR),
            container_filename=f"{db_name}.duckdb"
        )
