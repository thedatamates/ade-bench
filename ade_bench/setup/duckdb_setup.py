"""
DuckDB setup functions.
"""

from pathlib import Path
from typing import Dict, Any


def setup_duckdb(terminal, session, variant: Dict[str, Any]) -> None:
    """Setup DuckDB by copying the database file."""
    db_name = variant.get('db_name')
    if not db_name:
        return

    shared_db_path = Path(__file__).parent.parent.parent / "shared" / "databases" / "duckdb" / f"{db_name}.duckdb"
    if shared_db_path.exists():
        terminal.copy_to_container(paths=shared_db_path, container_dir="/app", container_filename=shared_db_path.name)
