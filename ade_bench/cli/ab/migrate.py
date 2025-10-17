"""Commands for database migration tasks."""

import typer
from pathlib import Path
from typing import Optional, List

app = typer.Typer(help="Database migration tools")


@app.command()
def duckdb_to_snowflake(
    include: Optional[List[str]] = typer.Option(
        None,
        "--include",
        "-i",
        help="DuckDB databases to include (e.g., airbnb, analytics_engineering)"
    ),
    exclude: Optional[List[str]] = typer.Option(
        None,
        "--exclude",
        "-e", 
        help="DuckDB databases to exclude"
    ),
    use_database_export: bool = typer.Option(
        False,
        "--use-database-export",
        help="Use database export for better performance"
    ),
):
    """
    Migrate DuckDB databases to Snowflake.
    """
    # Import the migration script
    from scripts_python.migrate_duckdb_to_snowflake import main as migrate_main
    
    # Call the migration function with the provided arguments
    migrate_main(include, exclude, use_database_export)


@app.command()
def setup_snowflake_task(
    task_id: str = typer.Argument(..., help="Task ID to set up in Snowflake"),
    db_name: str = typer.Argument(..., help="Database name to use in Snowflake"),
    config_path: Path = typer.Option(
        None,
        "--config-path",
        "-c",
        help="Path to configuration file (optional)"
    ),
):
    """
    Set up a Snowflake task environment.
    """
    # Import the setup script
    from scripts_python.setup_snowflake_task import main as setup_main
    
    # Call the setup function
    setup_main(task_id, db_name, config_path)


if __name__ == "__main__":
    app()