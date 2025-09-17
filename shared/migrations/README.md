# Migration Directories

This directory contains migration directories that can be used with task variants. Each migration directory contains a `migration.sh` script and any other files needed for the migration.

## Usage

Migration directories are referenced by name in the task variants configuration:

```yaml
variants:
- db_type: duckdb
  db_name: foo
  project_type: dbt
  project_name: foo
  migration_directory: my_migration
```

The directory `my_migration/` will be copied to the container and `migration.sh` will be executed before the setup script.

## Directory Requirements

- Must be a directory containing a `migration.sh` file
- The `migration.sh` file must be executable
- The entire directory will be copied to the container
- The `migration.sh` script will be run in the task environment before setup
- Should handle any necessary database or environment preparation
