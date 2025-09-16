"""
dbt setup functions.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from .setup_utils import generate_task_snowflake_credentials, update_file_in_container

def _update_snowflake_creds(path: str, project_name: str, task_id: str) -> None:
    """Update the profiles.yml file with task-specific Snowflake credentials."""
    profile_name = f"{project_name}-snowflake"
    creds = generate_task_snowflake_credentials(task_id)

    with open(path) as f:
        profiles = yaml.safe_load(f)

    profiles[profile_name]['outputs']['dev']['account'] = creds['account'].replace('.snowflakecomputing.com', '')
    profiles[profile_name]['outputs']['dev']['user'] = creds['user']
    profiles[profile_name]['outputs']['dev']['password'] = creds['password']
    profiles[profile_name]['outputs']['dev']['role'] = creds['role']
    profiles[profile_name]['outputs']['dev']['database'] = creds['database']
    profiles[profile_name]['outputs']['dev']['schema'] = creds['schema']
    profiles[profile_name]['outputs']['dev']['warehouse'] = creds['warehouse']

    with open(path, "w") as f:
        yaml.safe_dump(profiles, f)

def _update_project_profile(path: str, project_name: str, task_id: str) -> None:
    """Update the dbt_project.yml file with task-specific Snowflake credentials."""
    profile_name = f"{project_name}-snowflake"

    with open(path) as f:
        profiles = yaml.safe_load(f)

    profiles['profile'] = profile_name

    with open(path, "w") as f:
        yaml.safe_dump(profiles, f)

def _update_snowflake_files(session, project_name: str, task_id: str, project_dir: Path) -> None:
    # Update profiles.yml file with task-specific Snowflake credentials
    update_file_in_container(
        session.container,
        "/app/profiles.yml",
        _update_snowflake_creds,
        project_name,
        task_id
    )

    # Update dbt_project.yml file with task-specific Snowflake credentials
    update_file_in_container(
        session.container,
        "/app/dbt_project.yml",
        _update_project_profile,
        project_name,
        task_id
    )



def setup_dbt_project(terminal, session, task_id: str, variant: Dict[str, Any]) -> None:
    """Setup dbt project by copying project files."""
    project_name = variant.get('project_name')
    project_type = variant.get('project_type')

    if not project_name:
        return

    # Determine the project directory based on project_type
    project_type_path = 'dbt' if project_type == 'dbt-fusion' else project_type
    shared_project_dir = Path(__file__).parent.parent.parent / "shared" / "projects" / project_type_path / project_name

    if shared_project_dir.exists():
        terminal.copy_to_container(paths=shared_project_dir, container_dir="/app")

        if variant.get('db_type') == 'snowflake' and task_id:
            _update_snowflake_files(session, project_name, task_id, shared_project_dir)


