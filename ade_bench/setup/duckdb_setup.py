"""
DuckDB setup functions.
"""

from typing import Dict, Any, Tuple
from ..terminal.docker_compose_manager import DockerComposeManager


def setup_duckdb(terminal, session, variant: Dict[str, Any], trial_handler) -> Tuple[bool, str]:
    """Setup DuckDB by copying the database file.

    Returns:
        Tuple of (success, error_message). error_message is empty string on success.
    """
    db_name = variant.get('db_name')
    db_path = variant.get('db_path')

    if not db_name and not db_path:
        return True, ""

    shared_db_path = trial_handler.get_duckdb_file_path(db_name, db_path)

    if not shared_db_path.exists():
        if db_path:
            return False, f"DuckDB database not found at specified db_path: {shared_db_path.resolve()}"
        else:
            return False, f"DuckDB database '{db_name}' not found at {shared_db_path.resolve()}"

    # Use the filename from the path when db_path is specified
    container_filename = shared_db_path.name if db_path else f"{db_name}.duckdb"
    terminal.copy_to_container(
        paths=shared_db_path,
        container_dir=str(DockerComposeManager.CONTAINER_APP_DIR),
        container_filename=container_filename
    )
    return True, ""
