#!/usr/bin/env python3
"""
Snowflake task setup script.

This script:
1. Takes a task_id and source database as inputs
2. Clones the source database to create a new database named task_id
3. Creates a user and role for the new database
4. Grants the role appropriate permissions

Usage:
    # Run from outside the project directory to avoid module conflicts
    cd /tmp
    python /path/to/scripts_python/setup_snowflake_task.py --task-id <task_id> --source-db <source_database>

Requirements:
    - pip install snowflake-connector-python
    - Snowflake account with appropriate permissions
    - Note: Run from outside project directory due to local 'docker' folder conflict
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    import snowflake.connector
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    snowflake = None


class SnowflakeTaskSetup:
    """Setup Snowflake task with database cloning and user/role creation."""

    def __init__(self):
        self.snowflake_conn = None

    def _execute_queries(self, cursor, queries: str, description: str = ""):
        """Execute multiple SQL queries separated by semicolons."""
        for query in queries.split(";"):
            query = query.strip()
            if query:  # Skip empty queries
                print(f"  - {query}")
                cursor.execute(query)

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

    def clone_database(self, source_db: str, target_db: str) -> bool:
        """Clone a Snowflake database."""
        try:
            with self.get_snowflake_connection() as conn:
                cursor = conn.cursor()

                # Check if source database exists
                check_source_query = f"SHOW DATABASES LIKE '{source_db}'"
                print(f"  - {check_source_query}")
                cursor.execute(check_source_query)
                source_exists = cursor.fetchone() is not None

                if not source_exists:
                    print(f"  ❌ Source database '{source_db}' does not exist")
                    return False

                # Drop target database if it exists
                drop_target_query = f"DROP DATABASE IF EXISTS {target_db}"
                print(f"  - {drop_target_query}")
                cursor.execute(drop_target_query)

                # Clone the database
                clone_query = f"CREATE DATABASE {target_db} CLONE {source_db}"
                print(f"  - {clone_query}")
                cursor.execute(clone_query)
                print(f"  ✅ Successfully cloned database '{source_db}' to '{target_db}'")

                return True

        except Exception as e:
            print(f"  ❌ Error cloning database: {e}", file=sys.stderr)
            return False

    def create_user_and_role(self, task_id: str) -> bool:
        """Create user and role for the database."""
        try:
            with self.get_snowflake_connection() as conn:
                cursor = conn.cursor()

                # Create user with task_id as username (prefixed with ade_bench_)
                database_name = f"{task_id}"
                username = f"ade_bench_{task_id}".upper()
                role_name = f"{username}_ROLE"
                password = f"ade_bench_{task_id}_password_123"  # Simple password for demo

                # Use the target database
                use_db_query = f"USE DATABASE {database_name}"
                print(f"  - {use_db_query}")
                cursor.execute(use_db_query)

                # Drop and create role
                print(f"  Creating role: {role_name}")
                role_query = f"""
                    DROP ROLE IF EXISTS {role_name};
                    CREATE ROLE {role_name};
                """
                self._execute_queries(cursor, role_query)

                # Grant privileges to the role
                print(f"  Granting privileges to role {role_name}...")
                grants_query = f"""
                    GRANT USAGE ON DATABASE {database_name} TO ROLE {role_name};
                    GRANT CREATE SCHEMA ON DATABASE {database_name} TO ROLE {role_name};
                    GRANT USAGE, MODIFY ON ALL SCHEMAS IN DATABASE {database_name} TO ROLE {role_name};
                    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {database_name}.PUBLIC TO ROLE {role_name};
                """
                self._execute_queries(cursor, grants_query)

                # Drop and create user
                print(f"  Creating user: {username}")
                user_query = f"""
                    DROP USER IF EXISTS {username};
                    CREATE USER {username}
                    PASSWORD = '{password}'
                    DEFAULT_ROLE = {role_name};
                    GRANT ROLE {role_name} TO USER {username};
                """
                self._execute_queries(cursor, user_query)

                print(f"  ✅ Created/replaced user: {username} with role: {role_name}")
                print(f"  🔑 Password for {username}: {password}")
                return True

        except Exception as e:
            print(f"  ❌ Error creating user and role for {task_id}: {e}", file=sys.stderr)
            return False

    def setup_task(self, task_id: str, source_db: str) -> bool:
        """Setup a Snowflake task by cloning database and creating user/role."""
        print(f"Setting up Snowflake task '{task_id}'...")
        print(f"Source database: {source_db}")
        print(f"Target database: {task_id}")

        # Clone the database
        if not self.clone_database(source_db, task_id):
            print(f"❌ Failed to clone database '{source_db}' to '{task_id}'")
            return False

        # Create user and role
        if not self.create_user_and_role(task_id):
            print(f"❌ Failed to create user and role for '{task_id}'")
            return False

        print(f"✅ Successfully set up Snowflake task for '{task_id}'")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Setup Snowflake task by cloning database and creating user/role",
        add_help=False
    )

    parser.add_argument(
        "--task-id",
        required=True,
        help="Task ID (will be used as target database name and user prefix)"
    )

    parser.add_argument(
        "--source-db",
        required=True,
        help="Source database name to clone"
    )

    args = parser.parse_args()

    # Check if Snowflake is available
    if not SNOWFLAKE_AVAILABLE:
        print("Error: Snowflake connector not available. Please install snowflake-connector-python.", file=sys.stderr)
        sys.exit(1)

    # Create setup instance
    setup = SnowflakeTaskSetup()

    try:
        success = setup.setup_task(args.task_id, args.source_db)
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nSetup interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Setup failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
