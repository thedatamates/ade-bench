"""Commands for managing ADE-bench tasks."""

import os
import shlex
import logging
import typer
import yaml
import tempfile
import subprocess
from pathlib import Path
from typing import Annotated
from rich.console import Console
from rich.table import Table

from ade_bench.handlers.trial_handler import TrialHandler
from ade_bench.terminal.docker_compose_manager import DockerComposeManager
from ade_bench.utils.logger import logger

tasks_app = typer.Typer(help="Manage ADE-bench tasks")

@tasks_app.command()
def interact(
    task_id: Annotated[
        str, typer.Option("-t", "--task-id", help="The ID of the task to launch.")
    ],
    db: Annotated[
        str, typer.Option("--db", help="Database type to use (e.g., duckdb, snowflake)")
    ],
    project_type: Annotated[
        str, typer.Option("--project-type", help="Project type to use (e.g., dbt)")
    ],
    agent: Annotated[
        str, typer.Option("--agent", help="Agent to set up (optional)"),
    ] = None,
    tasks_dir: Annotated[
        Path, typer.Option(help="The path to the tasks directory.")
    ] = Path("tasks"),
    include_all: Annotated[
        bool,
        typer.Option(
            "-a",
            "--include-all",
            help="Copy test scripts and solution script to container",
        ),
    ] = False,
    rebuild: Annotated[
        bool, typer.Option(help="Whether to rebuild the client container.")
    ] = True,
    run_id: Annotated[
        str, typer.Option(help="Optional run ID for output directory")
    ] = None,
):
    """
    Launch an interactive shell into a task environment.
    
    This command sets up the task environment exactly like the harness would,
    then drops you into an interactive shell for debugging.
    """
    # Import necessary modules from harness
    from ade_bench import Harness
    from ade_bench.handlers.trial_handler import TrialHandler
    from ade_bench.setup.setup_orchestrator import SetupOrchestrator
    from ade_bench.agents import AgentName
    from ade_bench.utils.logger import logger
    from datetime import datetime
    
    # Set up logging
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    
    # Configure output directory
    output_path = Path("experiments")
    if not run_id:
        run_id = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    
    # Create the TrialHandler (this mimics what Harness does)
    task_dir = tasks_dir / task_id
    if not task_dir.exists():
        typer.echo(f"Task {task_dir.absolute()} does not exist.")
        raise typer.Exit(code=1)
        
    # Create the output directory
    output_dir = output_path / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the trial handler
    trial_handler = TrialHandler(
        trial_name=task_id,
        input_path=task_dir,
        output_path=output_dir
    )
    
    # Find the matching variant
    variant_found = False
    for variant in trial_handler.task.variants:
        if variant.db_type == db and variant.project_type == project_type:
            trial_handler.variant_config = variant.model_dump()
            variant_found = True
            break
    
    if not variant_found:
        typer.echo(f"No variant found for database '{db}' and project type '{project_type}'")
        typer.echo("Available variants:")
        for variant in trial_handler.task.variants:
            typer.echo(f"  - Database: {variant.db_type}, Project Type: {variant.project_type}")
        raise typer.Exit(code=1)
    
    # Set up Docker container using DockerComposeManager
    from ade_bench.terminal.docker_compose_manager import DockerComposeManager
    
    typer.echo(f"Setting up container for {task_id} with {db}/{project_type}...")
    docker_manager = DockerComposeManager(
        client_container_name=trial_handler.client_container_name,
        client_image_name=trial_handler.client_image_name,
        docker_compose_path=trial_handler.docker_compose_path,
        docker_name_prefix=trial_handler.docker_image_prefix,
        no_rebuild=not rebuild,
        cleanup=False,  # We don't want to clean up after
        logs_path=trial_handler.sessions_path,
        build_context_dir=trial_handler.input_path,
    )
    
    # Start the container
    container = docker_manager.start()
    
    # Create a terminal for setup operations
    from ade_bench.terminal.terminal import Terminal
    
    terminal = Terminal(
        client_container_name=trial_handler.client_container_name,
        client_image_name=trial_handler.client_image_name,
        docker_compose_path=trial_handler.docker_compose_path,
        docker_name_prefix=trial_handler.docker_image_prefix,
        sessions_path=trial_handler.sessions_path,
        no_rebuild=True,  # Already built
        cleanup=False,    # We'll handle cleanup
        build_context_dir=trial_handler.input_path,
    )
    # Set both the container and the compose manager's client container
    terminal.container = container
    terminal._compose_manager._client_container = container
    
    # Run task setup
    typer.echo("Setting up task environment...")
    setup_orchestrator = SetupOrchestrator(
        logger=logger,
        terminal=terminal,
        session=None,  # No tmux session needed for setup
        file_diff_handler=None,
        trial_handler=trial_handler
    )
    
    try:
        # Run database-specific and project-specific setup
        setup_orchestrator.setup_task(task_id, trial_handler.variant_config)
        
        # Set up agent if requested
        if agent:
            try:
                agent_name = AgentName(agent.lower())
                typer.echo(f"Setting up agent: {agent_name.value}")
                
                # Set agent in trial handler
                trial_handler.agent_name = agent_name
                
                from ade_bench.setup.agent_setup import setup_agent_config
                setup_agent_config(terminal, task_id, trial_handler, logger)
                
            except ValueError:
                typer.echo(f"Warning: Unknown agent '{agent}', skipping agent setup")
                typer.echo(f"Available agents: {', '.join([a.value for a in AgentName])}")
        
        # Copy solution/test files if requested
        if include_all:
            typer.echo("Copying solution and test files...")
            
            # Copy solutions directory if it exists
            if trial_handler.solutions_dir.exists():
                terminal.copy_to_container(
                    paths=[trial_handler.solutions_dir], 
                    container_dir="/solutions"
                )
            
            # Copy test files
            terminal.copy_to_container(
                paths=[
                    trial_handler.run_tests_path,
                    trial_handler.test_dir,
                ],
                container_dir="/tests"
            )
            
            # Copy solution.sh if it exists
            solution_script = task_dir / "solution.sh"
            if solution_script.exists():
                terminal.copy_to_container(
                    paths=[solution_script],
                    container_dir="/app",
                    container_filename="solution.sh"
                )
                
                # Make it executable
                container.exec_run("chmod +x /app/solution.sh")
        
        # Launch interactive shell
        typer.echo(f"\nInteractive environment ready for task {task_id}")
        typer.echo(f"Database: {db}, Project Type: {project_type}")
        if agent:
            typer.echo(f"Agent: {agent}")
        typer.echo("Type 'exit' to quit and clean up.")
        
        # Execute interactive shell
        subprocess.run(["docker", "exec", "-it", container.name, "bash"])
        
    finally:
        # Clean up
        typer.echo("Cleaning up container...")
        docker_manager.stop()

@tasks_app.command()
def list(
    tasks_dir: Annotated[
        Path, typer.Option(help="The path to the tasks directory.")
    ] = Path("tasks"),
):
    """List available tasks."""
    if not tasks_dir.exists():
        typer.echo(f"Tasks directory {tasks_dir} does not exist.")
        raise typer.Exit(code=1)
    
    # Get all task directories, excluding .template and any hidden directories
    tasks = [d for d in tasks_dir.iterdir() 
             if d.is_dir() and not d.name.startswith('.') and d.name != '.template']
    
    if not tasks:
        typer.echo("No tasks found.")
        raise typer.Exit(code=0)
    
    # Create a table
    table = Table(title="Available ADE-bench Tasks")
    table.add_column("Task ID", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    table.add_column("Variants", style="yellow")
    
    # Populate table with tasks
    for task_path in sorted(tasks):
        task_yaml = task_path / "task.yaml"
        if not task_yaml.exists():
            continue
            
        try:
            with open(task_yaml, "r") as f:
                task_data = yaml.safe_load(f)
                task_id = task_path.name
                description = task_data.get("description", "No description")
                
                # Format variants concisely
                variants = task_data.get("variants", [])
                variant_strs = []
                for v in variants:
                    db_type = v.get('db_type', '?')
                    proj_type = v.get('project_type', '?')
                    variant_strs.append(f"{db_type}/{proj_type}")
                
                variant_info = ", ".join(variant_strs)
                
                # Add a row to the table
                table.add_row(task_id, description, variant_info)
                
        except Exception as e:
            # Add error row
            table.add_row(task_path.name, f"[red]Error loading task.yaml[/red]", f"[red]{str(e)}[/red]")
    
    # Print the table
    console = Console()
    console.print(table)