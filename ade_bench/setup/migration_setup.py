"""
Migration setup functions.
"""

from pathlib import Path
from typing import Dict, Any


def setup_migration(terminal, session, variant: Dict[str, Any]) -> None:
    """Setup migration by copying migration files."""
    migration_directory = variant.get('migration_directory')

    if not migration_directory:
        return

    migration_dir_path = Path(__file__).parent.parent.parent / "shared" / "migrations" / migration_directory

    if migration_dir_path.exists():
        migration_script_path = migration_dir_path / "migration.sh"

        session.copy_to_container(migration_script_path, container_dir="/app", container_filename="migration.sh")
        terminal.copy_to_container(paths=migration_dir_path, container_dir="/app/migration")

        # Run migration script (if it was copied in step 3)
        session.send_keys(["bash /app/migration.sh", "Enter"], block=True)
        session.container.exec_run(["rm", "/app/migration.sh"])
        session.container.exec_run(["rm", "-rf", "/app/migration"])
