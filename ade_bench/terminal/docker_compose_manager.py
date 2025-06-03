"""Docker Compose manager adapted for dbt and database containers."""

import io
import subprocess
import tarfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Generator, List, Optional, Union

import docker
import docker.errors
from docker.models.containers import Container

from ade_bench.utils.env_model import EnvModel
from ade_bench.utils.logger import logger
from ade_bench.database import DatabasePoolManager, DatabaseType
from ade_bench.harness_models import DatabaseConfig


class DockerComposeEnvVars(EnvModel):
    """Environment variables for Docker Compose."""
    
    client_container_name: Optional[str] = None
    client_image_name: Optional[str] = None
    name_prefix: Optional[str] = None
    container_logs_path: Optional[str] = None
    test_dir: Optional[str] = None
    build_context_dir: Optional[str] = None
    dockerfile_path: Optional[str] = None
    logs_path: Optional[str] = None
    dbt_project_path: Optional[str] = None
    data_path: Optional[str] = None
    
    # Database configurations
    db_type: str = "duckdb"  # duckdb or postgres
    db_name: str = "analytics"
    db_user: str = "dbt_user"
    db_password: str = "dbt_pass"
    db_port: int = 5432


class DockerComposeManager:
    """Manages Docker Compose for dbt and database containers."""
    
    CONTAINER_LOGS_PATH = "/logs"
    CONTAINER_TEST_DIR = Path("/tests")
    CONTAINER_DBT_PROJECT_DIR = Path("/dbt_project")
    CONTAINER_DATA_DIR = Path("/data")

    def __init__(
        self,
        client_container_name: str,
        client_image_name: str,
        docker_compose_path: Path,
        docker_name_prefix: Optional[str] = None,
        no_rebuild: bool = False,
        cleanup: bool = False,
        logs_path: Optional[Path] = None,
        build_context_dir: Optional[Path] = None,
        dockerfile_path: Optional[Path] = None,
        dbt_project_path: Optional[Path] = None,
        data_path: Optional[Path] = None,
        db_config: Optional[Dict[str, str]] = None,
        database_config: Optional[DatabaseConfig] = None,
    ):
        """Initialize Docker Compose manager.
        
        Args:
            client_container_name: Name for the main dbt container
            client_image_name: Docker image for the dbt container
            docker_compose_path: Path to docker-compose.yaml
            docker_name_prefix: Prefix for all container names
            no_rebuild: Skip rebuilding images
            cleanup: Remove images and volumes on stop
            logs_path: Host path for logs
            build_context_dir: Build context for Dockerfile
            dbt_project_path: Host path to dbt project
            data_path: Host path to data files
            db_config: Database configuration (type, name, user, etc.)
            database_config: Database configuration from task.yaml
        """
        try:
            self._client = docker.from_env()
        except docker.errors.DockerException as e:
            raise RuntimeError(
                f"Error creating docker client: {e}\n"
                "Please ensure that Docker is installed and running."
            )

        self._client_container_name = client_container_name
        self._client_image_name = client_image_name
        self._docker_name_prefix = docker_name_prefix
        self._docker_compose_path = docker_compose_path
        self._no_rebuild = no_rebuild
        self._cleanup = cleanup
        self._client_container: Optional[Container] = None
        self._logs_path = logs_path
        self._build_context_dir = build_context_dir
        self._dockerfile_path = dockerfile_path
        self._dbt_project_path = dbt_project_path
        self._data_path = data_path
        self._db_config = db_config or {}
        self._database_config = database_config
        self._logger = logger.getChild(__name__)
        self._db_pool_manager = DatabasePoolManager()

    def _run_docker_compose_command(
        self, command: List[str]
    ) -> subprocess.CompletedProcess:
        """Run a docker-compose command with the appropriate environment variables."""
        env_vars = DockerComposeEnvVars(
            client_image_name=self._client_image_name,
            client_container_name=self._client_container_name,
            name_prefix=self._docker_name_prefix,
            container_logs_path=self.CONTAINER_LOGS_PATH,
            test_dir=str(self.CONTAINER_TEST_DIR),
            build_context_dir=(
                str(self._build_context_dir.absolute())
                if self._build_context_dir
                else None
            ),
            dockerfile_path=(
                str(self._dockerfile_path.absolute())
                if self._dockerfile_path
                else None
            ),
            logs_path=(
                str(self._logs_path.absolute()) if self._logs_path else None
            ),
            dbt_project_path=(
                str(self._dbt_project_path.absolute()) if self._dbt_project_path else None
            ),
            data_path=(
                str(self._data_path.absolute()) if self._data_path else "/tmp/ade_bench_data"
            ),
            **self._db_config  # Merge database config
        )
        
        env = env_vars.to_env_dict(include_os_env=True)

        full_command = [
            "docker",
            "compose",
            "-p",
            self._client_container_name,
            "-f",
            str(self._docker_compose_path.resolve().absolute()),
            *command,
        ]
        self._logger.debug(f"Running docker compose command: {' '.join(full_command)}")

        try:
            result = subprocess.run(
                full_command,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            return result
        except subprocess.CalledProcessError as e:
            self._logger.error(
                f"Docker compose command failed with exit code {e.returncode}"
            )
            self._logger.error(f"Command: {' '.join(full_command)}")

            if e.stdout:
                self._logger.error(f"STDOUT: {e.stdout}")

            if e.stderr:
                self._logger.error(f"STDERR: {e.stderr}")

            raise

    def start(self) -> Container:
        """Start the Docker Compose services and return the client container."""
        if not self._no_rebuild:
            self._run_docker_compose_command(["build"])

        self._run_docker_compose_command(["up", "-d"])

        # Wait for services to be ready
        self._wait_for_services()

        self._client_container = self._client.containers.get(
            self._client_container_name
        )

        return self._client_container

    def _wait_for_services(self) -> None:
        """Wait for all services to be healthy."""
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # Check if all services are healthy
                result = self._run_docker_compose_command(["ps", "--format", "json"])
                # Parse JSON output and check health status
                # For now, just wait a bit
                import time
                time.sleep(2)
                break
            except Exception as e:
                self._logger.debug(f"Waiting for services... {e}")
                attempt += 1
                if attempt >= max_attempts:
                    raise RuntimeError("Services failed to become healthy")
                import time
                time.sleep(1)

    def stop(self) -> None:
        """Stop and remove the docker compose services."""
        try:
            self._run_docker_compose_command(["down"])

            if self._cleanup:
                self._run_docker_compose_command(["down", "--rmi", "all", "--volumes"])
        except Exception as e:
            self._logger.error(f"Error cleaning up docker compose services: {e}")

    def init_database(self, container: Container) -> None:
        """Initialize the database with seed data if provided."""
        self._logger.info("Initializing database...")
        
        # Handle shared database if configured
        if self._database_config and self._database_config.source == "shared":
            self._init_shared_database(container)
        elif self._data_path and self._data_path.exists():
            self._init_local_database(container)
        else:
            self._logger.info("No database initialization needed")
    
    def _init_shared_database(self, container: Container) -> None:
        """Initialize database from shared pool."""
        if not self._database_config or not self._database_config.name:
            raise ValueError("Shared database name not specified")
        
        self._logger.info(f"Loading shared database: {self._database_config.name}")
        
        # Determine database type
        db_type_str = self._database_config.type or self._db_config.get("db_type", "duckdb")
        db_type = DatabaseType(db_type_str)
        
        # Find the shared database file directly
        db_path = self._db_pool_manager.find_database_file(
            name=self._database_config.name,
            db_type=db_type
        )
        
        if not db_path:
            raise FileNotFoundError(f"Database '{self._database_config.name}' of type {db_type.value} not found")
        
        # Copy database file directly to container
        self.copy_to_container(
            container=container,
            paths=db_path,
            container_dir=str(self.CONTAINER_DATA_DIR)
        )
        
        # Rename to expected name based on database type
        if db_type == DatabaseType.DUCKDB:
            container.exec_run(f"mv {self.CONTAINER_DATA_DIR}/{db_path.name} {self.CONTAINER_DATA_DIR}/analytics.duckdb")
        elif db_type == DatabaseType.SQLITE:
            container.exec_run(f"mv {self.CONTAINER_DATA_DIR}/{db_path.name} {self.CONTAINER_DATA_DIR}/analytics.db")
        elif db_type == DatabaseType.POSTGRES:
            # For PostgreSQL, the .sql file will be executed during container startup
            pass
        
        self._logger.info(f"Shared database '{self._database_config.name}' initialized successfully")
    
    def _init_local_database(self, container: Container) -> None:
        """Initialize database from local data files."""
        self._logger.info("Initializing database with local seed data...")
        
        # Copy data files to container
        self.copy_to_container(
            container=container,
            paths=self._data_path,
            container_dir=str(self.CONTAINER_DATA_DIR)
        )
        
        # Run initialization script based on database type
        db_type = self._db_config.get("db_type", "duckdb")
        
        if db_type == "duckdb":
            # For DuckDB, we might run SQL scripts to load data
            init_script = f"""
            cd {self.CONTAINER_DATA_DIR}
            for sql_file in *.sql; do
                if [ -f "$sql_file" ]; then
                    duckdb {self._db_config.get('db_name', 'analytics')}.duckdb < "$sql_file"
                fi
            done
            """
            container.exec_run(["sh", "-c", init_script])
        elif db_type == "sqlite":
            # For SQLite, run SQL scripts to load data
            init_script = f"""
            cd {self.CONTAINER_DATA_DIR}
            for sql_file in *.sql; do
                if [ -f "$sql_file" ]; then
                    sqlite3 {self._db_config.get('db_name', 'analytics')}.db < "$sql_file"
                fi
            done
            """
            container.exec_run(["sh", "-c", init_script])
        elif db_type == "postgres":
            # For PostgreSQL, connect and load data
            # This would be handled by the postgres container's init scripts
            pass

    @staticmethod
    def _create_tar_archive(
        paths: List[Path], container_filename: Optional[str]
    ) -> io.BytesIO:
        """Create a tar archive from the given paths."""
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            for path in paths:
                if path.is_file():
                    arcname = container_filename if container_filename else path.name
                    tar.add(path, arcname=arcname)
                elif path.is_dir():
                    for item in path.rglob("*"):
                        tar.add(item, arcname=item.relative_to(path))
                else:
                    raise ValueError(f"Path {path} is neither a file nor directory")

        tar_stream.seek(0)
        return tar_stream

    @staticmethod
    def copy_to_container(
        container: Container,
        paths: Union[List[Path], Path],
        container_dir: Optional[str] = None,
        container_filename: Optional[str] = None,
    ) -> None:
        """Copy files or directories to a running docker container."""
        container_dir = container_dir or container.attrs["Config"]["WorkingDir"]

        if container_dir is None:
            raise ValueError("Container working directory not found")

        if isinstance(paths, Path):
            paths = [paths]

        container.exec_run(f"mkdir -p {container_dir}")

        tar_stream = DockerComposeManager._create_tar_archive(paths, container_filename)
        container.put_archive(container_dir, tar_stream.read())
        tar_stream.close()

    def copy_to_client_container(
        self,
        paths: Union[List[Path], Path],
        container_dir: Optional[str] = None,
        container_filename: Optional[str] = None,
    ) -> None:
        """Copy files or directories to the client container."""
        if self._client_container is None:
            raise ValueError("Client container not started")

        return self.copy_to_container(
            container=self._client_container,
            paths=paths,
            container_dir=container_dir,
            container_filename=container_filename,
        )


@contextmanager
def spin_up_container(
    client_container_name: str,
    client_image_name: str,
    docker_compose_path: Path,
    docker_name_prefix: Optional[str] = None,
    no_rebuild: bool = False,
    cleanup: bool = False,
    logs_path: Optional[Path] = None,
    dbt_project_path: Optional[Path] = None,
    data_path: Optional[Path] = None,
    db_config: Optional[Dict[str, str]] = None,
) -> Generator[Container, None, None]:
    """Context manager for spinning up dbt and database containers."""
    container_manager = DockerComposeManager(
        client_container_name=client_container_name,
        client_image_name=client_image_name,
        docker_compose_path=docker_compose_path,
        no_rebuild=no_rebuild,
        cleanup=cleanup,
        logs_path=logs_path,
        docker_name_prefix=docker_name_prefix,
        dbt_project_path=dbt_project_path,
        data_path=data_path,
        db_config=db_config,
    )

    try:
        container = container_manager.start()
        # Initialize database if needed
        container_manager.init_database(container)
        yield container
    finally:
        container_manager.stop()