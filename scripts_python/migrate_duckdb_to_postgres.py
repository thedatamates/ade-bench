#!/usr/bin/env python3
"""
Comprehensive DuckDB to PostgreSQL migration script.

This script:
1. Discovers DuckDB files in specified directories
2. Analyzes schemas and tables in each DuckDB file
3. Converts DuckDB data to PostgreSQL seeds (excluding specified files)
4. Creates Docker images for each PostgreSQL seed

Usage:
    # Run from outside the project directory to avoid docker module conflict
    cd /tmp
    python /scripts_python/migrate_duckdb_to_postgres.py [options]

Requirements:
    - pip install docker duckdb psycopg2-binary
    - Running Docker daemon
    - Note: Run from outside project directory due to local 'docker' folder conflict
"""

import argparse
import os
import random
import string
import sys
import tempfile
import time
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

try:
    # Try to import docker package, avoiding local directory conflicts
    import sys
    import importlib.util

    # Check if we're in a directory with a local 'docker' folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    local_docker_dir = os.path.join(project_root, 'docker')

    if os.path.exists(local_docker_dir):
        # Temporarily remove the project root from sys.path to avoid conflicts
        original_path = sys.path[:]
        if project_root in sys.path:
            sys.path.remove(project_root)

        try:
            import docker as docker_lib
            DOCKER_AVAILABLE = True
        finally:
            # Restore original path
            sys.path = original_path
    else:
        import docker as docker_lib
        DOCKER_AVAILABLE = True

except ImportError:
    DOCKER_AVAILABLE = False
    docker_lib = None

import duckdb
from duckdb_utils import DuckDBExtractor

# Configuration - modify these paths as needed
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTGRES_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "shared", "databases", "postgres")
DEFAULT_PG_VERSION = "16"


class DuckDBToPostgresConverter:
    """Main converter class that handles the entire conversion pipeline."""

    def __init__(self, pg_version: str = DEFAULT_PG_VERSION):
        self.output_dir = Path(POSTGRES_OUTPUT_DIR).resolve()
        self.pg_version = pg_version
        self.docker_client = docker_lib.from_env() if DOCKER_AVAILABLE else None
        self.duckdb_extractor = DuckDBExtractor()

    def add_exclusions(self, exclusion_list: List[str]):
        """Add files to exclusion list."""
        self.duckdb_extractor.add_exclusions(exclusion_list)

    def discover_duckdb_files(self, patterns: List[str] = None) -> List[Path]:
        """Discover DuckDB files in the configured source directory."""
        return self.duckdb_extractor.discover_duckdb_files(patterns)

    def analyze_duckdb_schema(self, db_path: Path) -> Dict:
        """Analyze schema and tables in a DuckDB file."""
        return self.duckdb_extractor.analyze_duckdb_schema(db_path)

    def should_exclude_file(self, db_path: Path) -> bool:
        """Check if file should be excluded from conversion."""
        return self.duckdb_extractor.should_exclude_file(db_path)

    def should_include_file(self, db_path: Path, include_list: List[str]) -> bool:
        """Check if file should be included in conversion."""
        return self.duckdb_extractor.should_include_file(db_path, include_list)

    @contextmanager
    def temporary_postgres_container(self, db_name: str, port: int = None):
        """Context manager for temporary PostgreSQL container."""
        if not DOCKER_AVAILABLE:
            raise RuntimeError("Docker is not available. Please install docker package and ensure Docker daemon is running.")

        if port is None:
            port = random.randint(50000, 65000)

        container_name = f"pg_converter_{self._random_suffix()}"
        volume_name = f"pg_data_{self._random_suffix()}"

        # Create volume
        volume = self.docker_client.volumes.create(name=volume_name)

        try:
            # Start PostgreSQL container
            container = self.docker_client.containers.run(
                image=f"postgres:{self.pg_version}",
                name=container_name,
                detach=True,
                ports={"5432/tcp": port},
                environment={
                    "POSTGRES_USER": "postgres",
                    "POSTGRES_DB": db_name,
                    "POSTGRES_HOST_AUTH_METHOD": "trust",
                },
                volumes={
                    volume_name: {"bind": "/var/lib/postgresql/data", "mode": "rw"},
                },
            )

            # Wait for PostgreSQL to be ready
            self._wait_for_postgres_ready(container, port, timeout=60)

            yield container, port, volume_name

        finally:
            # Cleanup
            with suppress(Exception):
                container.stop()
                container.remove(force=True)
            with suppress(Exception):
                volume.remove(force=True)

    def _wait_for_postgres_ready(self, container, port: int, timeout: int = 60):
        """Wait for PostgreSQL container to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = container.exec_run([
                    "pg_isready", "-h", "localhost", "-p", "5432",
                    "-U", "postgres", "-d", "postgres"
                ])
                if result.exit_code == 0:
                    return
            except Exception:
                pass
            time.sleep(1)
        raise TimeoutError(f"PostgreSQL not ready after {timeout} seconds")

    def _random_suffix(self, length: int = 8) -> str:
        """Generate random suffix for container/volume names."""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def convert_duckdb_to_postgres_seed(self, duckdb_path: Path, seed_name: str = None) -> Optional[Path]:
        """Convert a DuckDB file to PostgreSQL seed tarball."""
        if seed_name is None:
            seed_name = duckdb_path.stem

        print(f"Converting {duckdb_path.name} to PostgreSQL seed...")

        # Analyze the DuckDB file first
        analysis = self.analyze_duckdb_schema(duckdb_path)
        if 'error' in analysis:
            print(f"Error analyzing {duckdb_path.name}: {analysis['error']}", file=sys.stderr)
            return None

        if analysis['total_tables'] == 0:
            print(f"No tables found in {duckdb_path.name}, skipping...", file=sys.stderr)
            return None

        try:
            with self.temporary_postgres_container("appdb") as (container, port, volume_name):
                # Connect to DuckDB and migrate data
                with duckdb.connect(str(duckdb_path), read_only=True) as duck_conn:
                    # Install and load postgres extension
                    duck_conn.execute("INSTALL postgres;")
                    duck_conn.execute("LOAD postgres;")

                    # Attach to PostgreSQL
                    duck_conn.execute(f"""
                        ATTACH 'host=127.0.0.1 port={port} dbname=appdb user=postgres'
                        AS pgdb (TYPE POSTGRES, READ_ONLY FALSE);
                    """)

                    # Create public schema if it doesn't exist
                    duck_conn.execute("CREATE SCHEMA IF NOT EXISTS pgdb.public;")

                    # Migrate each schema and its tables
                    for schema_name, schema_info in analysis['schemas'].items():
                        print(f"  Migrating schema '{schema_name}' with {schema_info['table_count']} tables...")

                        # Create schema in PostgreSQL
                        if schema_name != 'main':
                            duck_conn.execute(f"CREATE SCHEMA IF NOT EXISTS pgdb.{schema_name};")

                        # Migrate tables
                        for table_info in schema_info['tables']:
                            table_name = table_info['name']
                            print(f"    - {table_name}")

                            try:
                                # Drop table if exists
                                escaped_table = table_name.replace('"', '""')
                                if schema_name == 'main':
                                    duck_conn.execute(f'DROP TABLE IF EXISTS pgdb.public."{escaped_table}" CASCADE;')
                                    duck_conn.execute(f'CREATE TABLE pgdb.public."{escaped_table}" AS SELECT * FROM main."{escaped_table}";')
                                else:
                                    duck_conn.execute(f'DROP TABLE IF EXISTS pgdb.{schema_name}."{escaped_table}" CASCADE;')
                                    duck_conn.execute(f'CREATE TABLE pgdb.{schema_name}."{escaped_table}" AS SELECT * FROM {schema_name}."{escaped_table}";')

                            except Exception as e:
                                print(f"      Warning: Failed to migrate table {table_name}: {e}", file=sys.stderr)
                                # Continue with other tables

                # Stop container to ensure data is flushed
                print("Stopping PostgreSQL container...")
                container.stop()

                # Wait a moment for the container to fully stop
                import time
                time.sleep(2)

                # Create seed tarball
                print("Creating seed tarball...")
                seed_path = self._create_seed_tarball(volume_name, seed_name)
                return seed_path

        except Exception as e:
            print(f"Error converting {duckdb_path.name}: {e}", file=sys.stderr)
            return None

    def _create_seed_tarball(self, volume_name: str, seed_name: str) -> Path:
        """Create PostgreSQL seed tarball from volume."""
        tarball_name = f"pgseed-{self.pg_version}-{seed_name}.tgz"
        tarball_path = self.output_dir / "seeds" / tarball_name

        # Use Alpine container to create tarball with better error handling
        try:
            helper_container = self.docker_client.containers.run(
                image="alpine",
                command=["sh", "-c", """
                    echo "Checking PostgreSQL data directory..."
                    ls -la /var/lib/postgresql/data/
                    if [ -d "/var/lib/postgresql/data" ] && [ -f "/var/lib/postgresql/data/PG_VERSION" ]; then
                        echo "Found PostgreSQL data directory, creating tarball..."
                        cd /var/lib/postgresql && tar czf /out/pgseed.tgz data
                        echo "Tarball created successfully"
                    else
                        echo "PostgreSQL data directory not found or not initialized!"
                        echo "Contents of /var/lib/postgresql/data/:"
                        ls -la /var/lib/postgresql/data/ || echo "Directory does not exist"
                        exit 1
                    fi
                """],
                remove=True,
                volumes={
                    volume_name: {"bind": "/var/lib/postgresql/data", "mode": "ro"},
                    str(self.output_dir / "seeds"): {"bind": "/out", "mode": "rw"},
                },
                detach=False,
            )
        except Exception as e:
            print(f"Error creating tarball: {e}", file=sys.stderr)
            raise

        # Rename to final name
        temp_tarball = self.output_dir / "seeds" / "pgseed.tgz"
        if temp_tarball.exists():
            temp_tarball.rename(tarball_path)
            return tarball_path
        else:
            raise RuntimeError("Failed to create tarball - no output file found")

    def create_docker_image(self, seed_path: Path, image_tag: str = None) -> Optional[str]:
        """Create Docker image from PostgreSQL seed."""
        if not DOCKER_AVAILABLE:
            print("Warning: Docker not available, skipping image creation", file=sys.stderr)
            return None

        if image_tag is None:
            seed_name = seed_path.stem.replace(f"pgseed-{self.pg_version}-", "")
            image_tag = f"pgseed-{seed_name}:{self.pg_version}"

        print(f"Creating Docker image: {image_tag}")

        # Create temporary build context
        with tempfile.TemporaryDirectory(prefix="pgseed_build_") as build_dir:
            build_path = Path(build_dir)

            # Create Dockerfile
            dockerfile_content = f"""ARG PGVER={self.pg_version}
FROM postgres:${{PGVER}}
COPY pgseed.tgz /pgseed.tgz
COPY seed-entry.sh /usr/local/bin/seed-entry.sh
RUN chmod +x /usr/local/bin/seed-entry.sh
ENTRYPOINT ["bash", "/usr/local/bin/seed-entry.sh"]
CMD ["postgres"]
"""
            (build_path / "Dockerfile").write_text(dockerfile_content)

            # Create entry script
            entry_script = """#!/usr/bin/env bash
set -euo pipefail
DATA_DIR="/var/lib/postgresql/data"
if [ ! -s "$DATA_DIR/PG_VERSION" ]; then
  echo "Hydrating PGDATA from baked seed..."
  tar xzf /pgseed.tgz -C /var/lib/postgresql
  chown -R postgres:postgres "$DATA_DIR"
fi
exec /usr/local/bin/docker-entrypoint.sh "$@"
"""
            (build_path / "seed-entry.sh").write_text(entry_script)

            # Copy seed tarball
            import shutil
            shutil.copy2(seed_path, build_path / "pgseed.tgz")

            # Build image
            try:
                image, logs = self.docker_client.images.build(
                    path=str(build_path),
                    tag=image_tag,
                    rm=True
                )

                # Save image to file
                image_path = self.output_dir / "images" / f"{image_tag.replace(':', '_')}.tar"
                with open(image_path, 'wb') as f:
                    for chunk in image.save():
                        f.write(chunk)

                print(f"✅ Created image: {image_tag} -> {image_path}")
                return str(image_path)

            except Exception as e:
                print(f"Error creating Docker image {image_tag}: {e}", file=sys.stderr)
                return None

    def convert_all(self, exclusion_list: List[str] = None, include_list: List[str] = None) -> Dict:
        """Convert all discovered DuckDB files to PostgreSQL seeds and Docker images."""
        if exclusion_list:
            self.add_exclusions(exclusion_list)

        # Discover DuckDB files
        print(f"Discovering DuckDB files in {self.duckdb_extractor.source_dir}...")
        duckdb_files = self.discover_duckdb_files()
        print(f"Found {len(duckdb_files)} DuckDB files")

        # Filter files based on include/exclude logic
        filtered_files = self.duckdb_extractor.filter_files(duckdb_files, include_list)
        excluded_count = len(duckdb_files) - len(filtered_files)
        if excluded_count > 0:
            print(f"Excluded {excluded_count} files based on exclusion list")

        print(f"Processing {len(filtered_files)} files...")

        results = {
            'converted': [],
            'failed': [],
            'skipped': [],
            'total_discovered': len(duckdb_files),
            'total_processed': len(filtered_files)
        }

        # Process each file
        for i, duckdb_path in enumerate(filtered_files, 1):
            print(f"\n[{i}/{len(filtered_files)}] Processing {duckdb_path.name}...")

            # Convert to PostgreSQL seed
            seed_path = self.convert_duckdb_to_postgres_seed(duckdb_path)

            if seed_path is None:
                results['failed'].append(str(duckdb_path))
                continue

            # Create Docker image
            image_path = self.create_docker_image(seed_path)

            if image_path:
                results['converted'].append({
                    'duckdb_file': str(duckdb_path),
                    'seed_file': str(seed_path),
                    'image_file': image_path
                })
            else:
                results['failed'].append(str(duckdb_path))

        return results


def main():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[]
    )

    parser.add_argument(
        "--include",
        nargs="*",
        default=[]
    )

    parser.add_argument(
        "--dry-run",
        action="store_true"
    )

    args = parser.parse_args()

    # Create converter
    converter = DuckDBToPostgresConverter()

    if args.dry_run:
        # Just show what would be converted
        if args.exclude:
            converter.add_exclusions(args.exclude)

        duckdb_files = converter.discover_duckdb_files()

        if args.include:
            filtered_files = [f for f in duckdb_files if converter.should_include_file(f, args.include)]
            print(f"Would convert {len(filtered_files)} files (include mode):")
        else:
            filtered_files = [f for f in duckdb_files if not converter.should_exclude_file(f)]
            print(f"Would convert {len(filtered_files)} files (exclude mode):")

        for f in filtered_files:
            print(f"  - {f}")
        return

    # Perform conversion
    try:
        results = converter.convert_all(args.exclude, args.include)

        # Print summary
        print(f"\n{'='*60}")
        print("CONVERSION SUMMARY")
        print(f"{'='*60}")
        print(f"Total discovered: {results['total_discovered']}")
        print(f"Total processed: {results['total_processed']}")
        print(f"Successfully converted: {len(results['converted'])}")
        print(f"Failed: {len(results['failed'])}")

        if results['converted']:
            print(f"\nSuccessfully converted:")
            for item in results['converted']:
                print(f"  ✅ {Path(item['duckdb_file']).name}")

        if results['failed']:
            print(f"\nFailed conversions:")
            for item in results['failed']:
                print(f"  ❌ {Path(item).name}")


    except KeyboardInterrupt:
        print("\nConversion interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Conversion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
