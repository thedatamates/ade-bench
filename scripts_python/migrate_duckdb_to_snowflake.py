#!/usr/bin/env python3
"""
DuckDB to Snowflake migration script.

This script:
1. Discovers DuckDB files in specified directories
2. Analyzes schemas and tables in each DuckDB file
3. Creates Snowflake databases with the same name as DuckDB files
4. Loads data from DuckDB to Snowflake via Parquet files

Usage:
    # Run from outside the project directory to avoid module conflicts
    cd /tmp
    python /path/to/scripts_python/migrate_duckdb_to_snowflake.py [options]

Requirements:
    - pip install snowflake-connector-python duckdb pandas pyarrow
    - Snowflake account with appropriate permissions
    - Note: Run from outside project directory due to local 'docker' folder conflict
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Optional
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    import snowflake.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    snowflake = None

import pyarrow as pa
import pyarrow.parquet as pq
from duckdb_utils import DuckDBExtractor

# Configuration - modify these paths as needed
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNOWFLAKE_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "shared", "databases", "snowflake")


class DuckDBToSnowflakeConverter:
    """Main converter class that handles the entire conversion pipeline."""

    def __init__(self):
        self.output_dir = Path(SNOWFLAKE_OUTPUT_DIR).resolve()
        self.duckdb_extractor = DuckDBExtractor()
        self.snowflake_conn = None

        # Create output directory structure
        self.output_dir.mkdir(exist_ok=True)

    def _execute_queries(self, cursor, queries: str, description: str = ""):
        """Execute multiple SQL queries separated by semicolons."""
        for query in queries.split(";"):
            query = query.strip()
            if query:  # Skip empty queries
                print(f"  - {query}")
                cursor.execute(query)

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

    def get_snowflake_connection(self):
        """Get Snowflake connection using environment variables."""
        if not SNOWFLAKE_AVAILABLE:
            raise RuntimeError("Snowflake connector not available. Please install snowflake-connector-python.")

        # Get Snowflake credentials from environment
        account = os.getenv('SNOWFLAKE_ACCOUNT')
        user = os.getenv('SNOWFLAKE_USER')
        password = os.getenv('SNOWFLAKE_PASSWORD')

        if not all([account, user, password]):
            raise ValueError("Missing required Snowflake credentials. Please set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PASSWORD environment variables.")

        # Extract account identifier
        if '.snowflakecomputing.com' in account:
            account_id = account.replace('.snowflakecomputing.com', '')
        else:
            account_id = account

        conn = snowflake.connector.connect(
            account=account_id,
            user=user,
            password=password
        )

        return conn

    def create_snowflake_database(self, db_name: str) -> bool:
        """Create or replace a Snowflake database."""
        try:
            with self.get_snowflake_connection() as conn:
                cursor = conn.cursor()

                # Drop database if it exists, then create it
                create_db_query = f"""
                    DROP DATABASE IF EXISTS {db_name};
                    CREATE DATABASE {db_name};
                    USE DATABASE {db_name};
                """
                self._execute_queries(cursor, create_db_query)

                print(f"  ✅ Created/replaced database: {db_name}")

                return True

        except Exception as e:
            print(f"  ❌ Error creating database {db_name}: {e}", file=sys.stderr)
            return False


    def load_parquet_to_snowflake(self, parquet_path: Path, db_name: str, schema_name: str, table_name: str) -> bool:
        """Load a Parquet file into Snowflake."""
        try:
            with self.get_snowflake_connection() as conn:
                cursor = conn.cursor()

                # Use the target database
                stage_name = f"temp_stage_{table_name.lower()}"
                stage_query = f"""
                    USE DATABASE {db_name};
                    USE SCHEMA {schema_name};
                    CREATE OR REPLACE STAGE {stage_name};
                    PUT file://{parquet_path} @{stage_name};
                """
                self._execute_queries(cursor, stage_query)

                # Create table structure based on Parquet schema
                parquet_file = pq.ParquetFile(parquet_path)
                schema = parquet_file.schema_arrow

                # Convert Arrow schema to Snowflake DDL
                columns = []
                for field in schema:
                    sf_type = self._arrow_to_snowflake_type(field.type)
                    columns.append(f'"{field.name}" {sf_type}')

                ddl = f"""
                CREATE OR REPLACE TABLE {table_name} (
                    {', '.join(columns)}
                )
                """
                print(f"    - {ddl.strip()}")
                cursor.execute(ddl)
                print(f"    ✅ Created table structure: {table_name}")

                # Load data from stage into table using COPY INTO
                copy_query = f"""
                COPY INTO {table_name}
                FROM @{stage_name}/{parquet_path.name}
                FILE_FORMAT = (TYPE = 'PARQUET')
                MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
                ON_ERROR = 'CONTINUE'
                """
                print(f"    - {copy_query.strip()}")
                cursor.execute(copy_query)

                # Verify data was loaded
                count_query = f'SELECT COUNT(*) FROM {table_name}'
                print(f"    - {count_query}")
                cursor.execute(count_query)
                count = cursor.fetchone()[0]
                print(f"    ✅ Loaded {count} rows into {table_name}")

                # Clean up stage
                drop_stage_query = f"DROP STAGE IF EXISTS {stage_name}"
                print(f"    - {drop_stage_query}")
                cursor.execute(drop_stage_query)

                return True

        except Exception as e:
            print(f"    ❌ Error loading {table_name} to Snowflake: {e}", file=sys.stderr)
            return False

    def _extract_table_name(self, parquet_filename: str) -> str:
        """Extract table name from Parquet filename."""
        # Format: {db_name}_main_{table_name}.parquet
        # We want just the table name (the part after the last underscore before .parquet)
        name_without_ext = parquet_filename.replace('.parquet', '')

        # Split by underscores and find where 'main' is
        parts = name_without_ext.split('_')
        try:
            main_index = parts.index('main')
            if main_index + 1 < len(parts):
                # Return everything after 'main'
                return '_'.join(parts[main_index + 1:])
        except ValueError:
            pass

        # Fallback: use filename without extension
        return name_without_ext

    def _arrow_to_snowflake_type(self, arrow_type) -> str:
        """Convert Arrow type to Snowflake type."""
        type_mapping = {
            pa.int8(): "TINYINT",
            pa.int16(): "SMALLINT",
            pa.int32(): "INTEGER",
            pa.int64(): "BIGINT",
            pa.uint8(): "TINYINT",
            pa.uint16(): "SMALLINT",
            pa.uint32(): "INTEGER",
            pa.uint64(): "BIGINT",
            pa.float32(): "FLOAT",
            pa.float64(): "DOUBLE",
            pa.string(): "VARCHAR",
            pa.binary(): "BINARY",
            pa.bool_(): "BOOLEAN",
            pa.date32(): "DATE",
            pa.timestamp('ns'): "TIMESTAMP_NTZ",
            pa.timestamp('us'): "TIMESTAMP_NTZ",
            pa.timestamp('ms'): "TIMESTAMP_NTZ",
            pa.timestamp('s'): "TIMESTAMP_NTZ",
        }

        return type_mapping.get(arrow_type, "VARCHAR")

    def convert_duckdb_to_snowflake(self, duckdb_path: Path, db_name: str = None) -> Optional[Dict]:
        """Convert a DuckDB file to Snowflake database."""
        if db_name is None:
            db_name = duckdb_path.stem

        print(f"Converting {duckdb_path.name} to Snowflake database '{db_name}'...")

        # Analyze the DuckDB file first
        analysis = self.analyze_duckdb_schema(duckdb_path)
        if 'error' in analysis:
            print(f"Error analyzing {duckdb_path.name}: {analysis['error']}", file=sys.stderr)
            return None

        if analysis['total_tables'] == 0:
            print(f"No tables found in {duckdb_path.name}, skipping...", file=sys.stderr)
            return None

        results = {
            'database': db_name,
            'duckdb_file': str(duckdb_path),
            'tables_exported': 0,
            'tables_loaded': 0,
            'errors': []
        }

        try:
            # Create Snowflake database
            if not self.create_snowflake_database(db_name):
                results['errors'].append("Failed to create database")
                return results

            # Create database-specific directory for Parquet files
            db_parquet_dir = self.output_dir / db_name
            db_parquet_dir.mkdir(exist_ok=True)

            # Export all tables to Parquet using shared utility
            parquet_results = self.duckdb_extractor.export_all_tables_to_parquet(
                duckdb_path,
                db_parquet_dir,
                db_name
            )

            if not parquet_results['success']:
                results['errors'].append(parquet_results['error'])
                return results

            results['tables_exported'] = parquet_results['tables_exported']

            # Load each Parquet file to Snowflake
            for parquet_info in parquet_results['parquet_files']:
                schema_name = parquet_info['schema']
                parquet_path = Path(parquet_info['file_path'])

                # Extract table name from Parquet filename
                table_name = self._extract_table_name(parquet_path.name)

                print(f"    Loading {table_name} to Snowflake...")

                target_schema = "PUBLIC" if schema_name == "main" else schema_name
                if self.load_parquet_to_snowflake(parquet_path, db_name, target_schema, table_name):
                    results['tables_loaded'] += 1

            return results

        except Exception as e:
            print(f"Error converting {duckdb_path.name}: {e}", file=sys.stderr)
            results['errors'].append(str(e))
            return results

    def convert_all(self, exclusion_list: List[str] = None, include_list: List[str] = None) -> Dict:
        """Convert all discovered DuckDB files to Snowflake databases."""
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

            # Convert to Snowflake
            conversion_result = self.convert_duckdb_to_snowflake(duckdb_path)

            if conversion_result is None or conversion_result.get('errors'):
                results['failed'].append({
                    'duckdb_file': str(duckdb_path),
                    'errors': conversion_result.get('errors', ['Unknown error']) if conversion_result else ['Conversion failed']
                })
                continue

            results['converted'].append(conversion_result)

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

    # Check if Snowflake is available
    if not SNOWFLAKE_AVAILABLE:
        print("Error: Snowflake connector not available. Please install snowflake-connector-python.", file=sys.stderr)
        sys.exit(1)

    # Create converter
    converter = DuckDBToSnowflakeConverter()

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
                print(f"  ✅ {item['database']} ({item['tables_exported']} tables exported, {item['tables_loaded']} loaded)")

        if results['failed']:
            print(f"\nFailed conversions:")
            for item in results['failed']:
                print(f"  ❌ {Path(item['duckdb_file']).name}: {', '.join(item['errors'])}")

    except KeyboardInterrupt:
        print("\nConversion interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Conversion failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
