"""Handler for individual trial execution."""

from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Optional

from docker.models.containers import Container

from ade_bench.config import config
from ade_bench.terminal.docker_compose_manager import DockerComposeManager
from ade_bench.utils.logger import logger


class TrialHandler:
    """Handles the execution of a single trial."""
    
    def __init__(
        self,
        task: Any,
        output_path: Path,
        no_rebuild: bool = False,
        cleanup: bool = False,
    ):
        """Initialize trial handler.
        
        Args:
            task: Task object with metadata
            output_path: Path for trial outputs
            no_rebuild: Skip Docker rebuilds
            cleanup: Clean up Docker resources
        """
        self.task = task
        self.output_path = output_path
        self.no_rebuild = no_rebuild
        self.cleanup = cleanup
        self._logger = logger.getChild("trial_handler")
        
        # Create output directory
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def task_path(self) -> Path:
        """Path to task directory."""
        return config.tasks_dir / self.task.task_id
    
    @property
    def docker_compose_path(self) -> Path:
        """Path to docker-compose file for task."""
        task_compose = self.task_path / "docker-compose.yaml"
        
        if task_compose.exists():
            return task_compose
        
        # Use default based on database type
        db_type = getattr(self.task, "db_type", "duckdb")
        
        if db_type == "postgres":
            return config.shared_dir / "defaults" / "docker-compose-postgres.yaml"
        elif db_type == "sqlite":
            return config.shared_dir / "defaults" / "docker-compose-sqlite.yaml"
        elif db_type == "duckdb":
            return config.shared_dir / "defaults" / "docker-compose-duckdb.yaml"
        else:
            return config.shared_dir / "defaults" / "docker-compose.yaml"
    
    @property
    def dockerfile_path(self) -> Path:
        """Path to Dockerfile for task."""
        task_dockerfile = self.task_path / "Dockerfile"
        
        if task_dockerfile.exists():
            return task_dockerfile
        
        # Use default based on database type
        db_type = getattr(self.task, "db_type", "duckdb")
        
        if db_type == "postgres":
            return config.docker_dir / "base" / "Dockerfile.dbt-postgres"
        elif db_type == "sqlite":
            return config.docker_dir / "base" / "Dockerfile.dbt-sqlite"
        else:
            return config.docker_dir / "base" / "Dockerfile.dbt-duckdb"
    
    def setup(self) -> None:
        """Set up the trial environment."""
        self._logger.info(f"Setting up trial for task {self.task.task_id}")
        
        # Create logs directory
        logs_dir = self.output_path / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Copy any required files to output
        # This could include test results, configs, etc.
    
    @contextmanager
    def spin_up_containers(self) -> Generator[Container, None, None]:
        """Spin up Docker containers for the trial.
        
        Yields:
            The main client container
        """
        # Prepare database configuration
        db_config = {
            "db_type": getattr(self.task, "db_type", "duckdb"),
            "db_name": getattr(self.task, "db_name", "analytics"),
            "db_user": getattr(self.task, "db_user", "dbt_user"),
            "db_password": getattr(self.task, "db_password", "dbt_pass"),
        }
        
        # Container naming
        container_name = f"ade_{self.task.task_id}_{self.output_path.name}"
        image_name = f"ade-bench/{self.task.task_id}"
        name_prefix = f"ade_{self.task.task_id}"
        
        # Paths
        dbt_project_path = self.task_path / "dbt_project"
        data_path = self.task_path / "data"
        logs_path = self.output_path / "logs"
        
        # For shared databases, we still need a data path for the container
        # even though we won't use local data files
        if not data_path.exists() and hasattr(self.task, "database") and self.task.database:
            # Use a temporary directory for the data volume
            data_path = self.output_path / "data"
            data_path.mkdir(exist_ok=True)
        
        # Create Docker Compose manager
        manager = DockerComposeManager(
            client_container_name=container_name,
            client_image_name=image_name,
            docker_compose_path=self.docker_compose_path,
            docker_name_prefix=name_prefix,
            no_rebuild=self.no_rebuild,
            cleanup=self.cleanup,
            logs_path=logs_path,
            build_context_dir=config.project_root,  # Use project root as context
            dockerfile_path=self.dockerfile_path,
            dbt_project_path=dbt_project_path if dbt_project_path.exists() else None,
            data_path=data_path,  # Always provide a data path
            db_config=db_config,
            database_config=getattr(self.task, "database", None),
        )
        
        try:
            # Start containers
            self._logger.info(f"Starting containers for {self.task.task_id}")
            container = manager.start()
            
            # Copy test files to container if they exist
            test_dir = self.task_path / "tests"
            if test_dir.exists():
                manager.copy_to_client_container(
                    paths=test_dir,
                    container_dir="/tests",
                )
            
            # Copy expected results if they exist
            expected_dir = self.task_path / "expected"
            if expected_dir.exists():
                manager.copy_to_client_container(
                    paths=expected_dir,
                    container_dir="/expected",
                )
            
            yield container
            
        finally:
            # Stop containers
            self._logger.info(f"Stopping containers for {self.task.task_id}")
            manager.stop()
    
    def get_results(self) -> Dict[str, Any]:
        """Get results from the trial.
        
        Returns:
            Dictionary of trial results
        """
        results = {
            "task_id": self.task.task_id,
            "output_path": str(self.output_path),
        }
        
        # Add logs if available
        log_files = list((self.output_path / "logs").glob("*.log"))
        if log_files:
            results["logs"] = [str(f) for f in log_files]
        
        return results