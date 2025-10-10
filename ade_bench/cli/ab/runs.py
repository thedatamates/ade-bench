"""Commands for managing ADE-bench runs."""

import typer
from pathlib import Path
from typing import Optional, List

app = typer.Typer(help="Manage ADE-bench runs")


@app.command()
def list(
    limit: int = typer.Option(
        10,
        "--limit",
        "-n",
        help="Number of runs to show"
    ),
    output_path: Path = typer.Option(
        Path("experiments"),
        "--output-path",
        "-o",
        help="Path to the output directory"
    ),
):
    """
    List recent benchmark runs.
    """
    if not output_path.exists():
        typer.echo(f"Output directory {output_path} does not exist.")
        raise typer.Exit(code=1)
    
    # Get all directories in the output path
    runs = sorted(
        [d for d in output_path.iterdir() if d.is_dir()], 
        key=lambda d: d.stat().st_mtime, 
        reverse=True
    )
    
    if not runs:
        typer.echo("No runs found.")
        raise typer.Exit(code=0)
    
    # Limit the number of runs to show
    runs = runs[:limit]
    
    # Print the runs
    typer.echo(f"Recent {len(runs)} ADE-bench runs:")
    for i, run in enumerate(runs, 1):
        results_file = run / "results.json"
        metadata_file = run / "run_metadata.json"
        
        if results_file.exists() and metadata_file.exists():
            import json
            try:
                with open(results_file, "r") as f:
                    results = json.load(f)
                    accuracy = results.get("accuracy", "N/A")
                    
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    agent = metadata.get("agent_name", "N/A")
                    db_type = metadata.get("db_type", "N/A")
                    
                typer.echo(f"{i}. {run.name} - Agent: {agent}, Accuracy: {accuracy}")
            except json.JSONDecodeError:
                typer.echo(f"{i}. {run.name} - Could not parse results")
        else:
            typer.echo(f"{i}. {run.name} - Incomplete run")


@app.command()
def open(
    run_id: Optional[str] = typer.Argument(
        None,
        help="Run ID to open. If not provided, opens the most recent run."
    ),
    output_path: Path = typer.Option(
        Path("experiments"),
        "--output-path",
        "-o",
        help="Path to the output directory"
    ),
):
    """
    Open a specific run in your browser.
    """
    if not output_path.exists():
        typer.echo(f"Output directory {output_path} does not exist.")
        raise typer.Exit(code=1)
    
    if run_id:
        run_path = output_path / run_id
        if not run_path.exists():
            typer.echo(f"Run {run_id} not found.")
            raise typer.Exit(code=1)
    else:
        # Get the most recent run
        runs = sorted(
            [d for d in output_path.iterdir() if d.is_dir()], 
            key=lambda d: d.stat().st_mtime, 
            reverse=True
        )
        
        if not runs:
            typer.echo("No runs found.")
            raise typer.Exit(code=1)
        
        run_path = runs[0]
    
    # Look for the results HTML file
    html_file = run_path / "index.html"
    if not html_file.exists():
        typer.echo(f"Results HTML not found for run {run_path.name}.")
        raise typer.Exit(code=1)
    
    # Open the HTML file in the default browser
    import webbrowser
    webbrowser.open(f"file://{html_file.absolute()}")
    typer.echo(f"Opened {html_file} in your browser.")


if __name__ == "__main__":
    app()