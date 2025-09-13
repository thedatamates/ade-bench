# DuckDB to PostgreSQL Migration

This directory contains a comprehensive script for migrating DuckDB files to PostgreSQL seeds and Docker images.


## Overview

The converter performs the following operations:

1. **Discovery**: Finds DuckDB files in specified directories
2. **Analysis**: Analyzes schemas and tables in each DuckDB file
3. **Conversion**: Converts DuckDB data to PostgreSQL seeds (excluding specified files)
4. **Docker Images**: Creates Docker images for each PostgreSQL seed

## Quick Start

### Basic Usage

```bash
# Convert all DuckDB files (reads from shared/databases/duckdb/)
# Run from outside project directory to avoid module conflicts
uv run scripts_python/migrate_duckdb_to_postgres.py

# Dry run to see what would be converted
uv run scripts_python/migrate_duckdb_to_postgres.py --dry-run

# Convert with exclusions
uv run scripts_python/migrate_duckdb_to_postgres.py --exclude workday test

# Convert only specific files
uv run scripts_python/migrate_duckdb_to_postgres.py --include activity airbnb
```

### Advanced Usage

```bash
# No additional options - script is fully self-contained
```

## Output Structure

The converter creates the following directory structure:

```
shared/databases/postgres/
├── seeds/
│   ├── pgseed-16-activity.tgz
│   ├── pgseed-16-airbnb.tgz
│   └── ...
├── images/
│   ├── pgseed-activity_16.tar
│   ├── pgseed-airbnb_16.tar
│   └── ...
└── conversion_results.json
```

## Features

### Simple Configuration
- Reads from `shared/databases/duckdb/` by default
- Writes to `shared/databases/postgres/` by default
- Configurable paths at the top of the script

### Schema Analysis
- Analyzes all schemas in DuckDB files
- Counts tables per schema
- Handles multiple schemas (not just 'main')

### Simple Filtering
- **Exclude mode**: Convert all files except specified ones
- **Include mode**: Convert only specified files
- Flexible matching (filename or stem)

### Robust Conversion
- Uses DuckDB's PostgreSQL extension for data migration
- Handles column type conversions automatically
- Creates proper PostgreSQL schemas
- Preserves table relationships

### Docker Integration
- Creates PostgreSQL seed tarballs
- Builds Docker images with custom entry scripts
- Saves images as tar files for distribution
- Supports different PostgreSQL versions

### Error Handling
- Graceful handling of conversion errors
- Continues processing other files if one fails
- Detailed error reporting
- Comprehensive logging

## Requirements

- Python 3.10+
- Docker daemon running
- Required packages: `docker`, `duckdb`, `psycopg2-binary`

## Usage Note

The script uses absolute paths, so it can be run from anywhere. It automatically finds the project directories based on the script's location.

**Important**: Due to a local `docker/` directory in the project, the script should be run from outside the project directory to avoid module import conflicts. The script automatically handles this when run from external directories.

## Programmatic Usage

You can also use the converter programmatically:

```python
from migrate_duckdb_to_postgres import DuckDBToPostgresConverter

# Create converter
converter = DuckDBToPostgresConverter()

# Add exclusions
converter.add_exclusions(["test", "debug"])

# Discover files
files = converter.discover_duckdb_files()

# Analyze a file
analysis = converter.analyze_duckdb_schema(files[0])

# Convert all files
results = converter.convert_all(["workday"], ["activity", "airbnb"])
```

## Example Output

```
Discovering DuckDB files...
Found 8 DuckDB files
Excluded 1 files based on exclusion list
Processing 7 files...

[1/7] Processing activity.duckdb...
Converting activity.duckdb to PostgreSQL seed...
  Migrating schema 'main' with 29 tables...
    - example__activity_stream
    - input__aggregate_after
    - input__aggregate_all_ever
    ...
>> Stopping Postgres and snapshotting PGDATA ...
✅ Seed tarball written: shared_databases_postgres/seeds/pgseed-16-activity.tgz
Creating Docker image: pgseed-activity:16
✅ Created image: pgseed-activity:16 -> shared_databases_postgres/images/pgseed-activity_16.tar

============================================================
CONVERSION SUMMARY
============================================================
Total discovered: 8
Total processed: 7
Successfully converted: 7
Failed: 0

Successfully converted:
  ✅ activity.duckdb
  ✅ airbnb.duckdb
  ✅ analytics_engineering.duckdb
  ✅ asana.duckdb
  ✅ f1.duckdb
  ✅ intercom.duckdb
  ✅ quickbooks.duckdb

Detailed results saved to: shared_databases_postgres/conversion_results.json
```

## Troubleshooting

### Docker Not Available
If Docker is not available, the script will skip image creation but still create PostgreSQL seeds.

### Module Import Errors
The script now uses absolute paths and should work from any directory.

### Permission Issues
Ensure the script has write permissions to the output directory.

### Large Files
For very large DuckDB files, the conversion may take time. Monitor Docker container resources.

## Integration with ADE-Bench

The generated PostgreSQL seeds and Docker images can be used in the ADE-Bench harness by:

1. Placing seed files in the appropriate directory
2. Loading Docker images into the registry
3. Configuring tasks to use PostgreSQL instead of DuckDB
4. Updating task configurations to reference the new database sources
