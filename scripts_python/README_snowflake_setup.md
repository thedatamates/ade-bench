# DuckDB to Snowflake Migration

This directory contains a comprehensive script for migrating DuckDB files to Snowflake databases.

## Files

- `migrate_duckdb_to_snowflake.py` - Main Snowflake migration script
- `duckdb_utils.py` - Shared DuckDB extraction utilities
- `README_snowflake_setup.md` - This documentation

## Overview

The Snowflake setup script performs the following operations:

1. **Discovery**: Finds DuckDB files in specified directories
2. **Analysis**: Analyzes schemas and tables in each DuckDB file
3. **Database Creation**: Creates or replaces Snowflake databases with the same name as DuckDB files
4. **Data Export**: Exports data from DuckDB to Parquet files for clean data transfer
5. **Data Loading**: Loads Parquet data into Snowflake tables (replaces existing tables)
6. **User Creation**: Creates or replaces Snowflake users for each database with appropriate permissions

## Quick Start

### Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install snowflake-connector-python pyarrow
   ```

2. **Set up Snowflake Credentials**:
   Create a `.env` file in the project root with your Snowflake credentials:
   ```bash
   # Snowflake Settings
   SNOWFLAKE_ACCOUNT=your-account.snowflakecomputing.com
   SNOWFLAKE_USER=your-username
   SNOWFLAKE_PASSWORD=your-password
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_ROLE=ACCOUNTADMIN
   SNOWFLAKE_DATABASE=
   SNOWFLAKE_SCHEMA=PUBLIC
   ```

3. **Ensure Snowflake Permissions**:
   Your Snowflake user needs the following permissions:
   - `CREATE DATABASE`
   - `CREATE USER`
   - `GRANT` privileges
   - Access to a warehouse for data loading

### Basic Usage

```bash
# Convert all DuckDB files (reads from shared/databases/duckdb/)
# Run from outside project directory to avoid module conflicts
cd /tmp
python3 /path/to/scripts_python/migrate_duckdb_to_snowflake.py

# Dry run to see what would be converted
python3 /path/to/scripts_python/migrate_duckdb_to_snowflake.py --dry-run

# Convert with exclusions
python3 /path/to/scripts_python/migrate_duckdb_to_snowflake.py --exclude workday test

# Convert only specific files
python3 /path/to/scripts_python/migrate_duckdb_to_snowflake.py --include activity airbnb
```

## Output Structure

The script creates the following directory structure:

```
shared/databases/snowflake/
├── parquet/
│   ├── activity_main_table1.parquet
│   ├── activity_main_table2.parquet
│   └── ...
├── logs/
│   └── conversion_results.json
```

## Features

### Simple Configuration
- Reads from `shared/databases/duckdb/` by default
- Writes to `shared/databases/snowflake/` by default
- Uses environment variables for Snowflake credentials

### Schema Analysis
- Analyzes all schemas in DuckDB files
- Counts tables per schema
- Handles multiple schemas (not just 'main')

### Clean Data Transfer
- Exports data to Parquet format for optimal Snowflake loading
- Preserves data types and handles type conversions
- Creates proper Snowflake table schemas

### Database Management
- Creates Snowflake databases with same names as DuckDB files
- Creates users for each database with appropriate permissions
- Handles schema creation and table structure

### User Management
- Creates users named after the database
- Grants appropriate privileges (USAGE, SELECT, etc.)
- Sets up default warehouse and role

### Error Handling
- Graceful handling of conversion errors
- Continues processing other files if one fails
- Detailed error reporting and logging
- Comprehensive conversion results

## Database and User Creation

For each DuckDB file, the script:

1. **Replaces Database**: `DROP DATABASE IF EXISTS {db_name}` then `CREATE DATABASE {db_name}`
2. **Replaces Schema**: `DROP SCHEMA IF EXISTS PUBLIC` then `CREATE SCHEMA PUBLIC`
3. **Replaces User**: `DROP USER IF EXISTS {db_name.upper()}` then `CREATE USER {db_name.upper()}`
4. **Grants Privileges**:
   - `GRANT USAGE ON DATABASE {db_name} TO {user}`
   - `GRANT USAGE ON SCHEMA {db_name}.PUBLIC TO {user}`
   - `GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {db_name}.PUBLIC TO {user}`
   - `GRANT ALL PRIVILEGES ON ALL FUTURE TABLES IN SCHEMA {db_name}.PUBLIC TO {user}`

## Data Loading Process

1. **Export to Parquet**: Each table is exported from DuckDB to a Parquet file
2. **Type Mapping**: Arrow types are mapped to appropriate Snowflake types
3. **Table Creation**: Snowflake tables are created or replaced with proper schema using `CREATE OR REPLACE TABLE`
4. **Data Loading**: Parquet files are prepared for loading (manual upload required)

**Note**: The current implementation creates the table structure and Parquet files. For production use, you may want to implement automatic file upload to Snowflake stages.

## Requirements

- Python 3.10+
- Snowflake account with appropriate permissions
- Required packages: `snowflake-connector-python`, `pyarrow`, `duckdb`, `pandas`

## Usage Note

The script uses absolute paths, so it can be run from anywhere. It automatically finds the project directories based on the script's location.

**Important**: Due to a local `docker/` directory in the project, the script should be run from outside the project directory to avoid module import conflicts.

## Programmatic Usage

You can also use the converter programmatically:

```python
from migrate_duckdb_to_snowflake import DuckDBToSnowflakeConverter

# Create converter
converter = DuckDBToSnowflakeConverter()

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
Converting activity.duckdb to Snowflake database 'activity'...
  ✅ Created/replaced database: activity
  ✅ Created/replaced schema: PUBLIC in activity
  ✅ Created/replaced user: ACTIVITY
  ✅ Granted privileges to user: ACTIVITY
  Processing schema 'main' with 29 tables...
    Processing table: example__activity_stream
    ✅ Exported example__activity_stream (1000 rows) -> activity_main_example__activity_stream.parquet
    ℹ️  Parquet file ready for upload: /path/to/activity_main_example__activity_stream.parquet
    ℹ️  Use Snowflake UI or SnowSQL to upload /path/to/activity_main_example__activity_stream.parquet to stage temp_stage_example__activity_stream
    ✅ Created table structure: example__activity_stream
    ...

============================================================
CONVERSION SUMMARY
============================================================
Total discovered: 8
Total processed: 7
Successfully converted: 7
Failed: 0

Successfully converted:
  ✅ activity (29 tables exported, 29 loaded)
  ✅ airbnb (15 tables exported, 15 loaded)
  ✅ analytics_engineering (8 tables exported, 8 loaded)
  ...

Detailed results saved to: /path/to/snowflake/logs/conversion_results.json
```

## Troubleshooting

### Missing Snowflake Credentials
Ensure all required environment variables are set in your `.env` file.

### Permission Issues
Make sure your Snowflake user has the necessary permissions to create databases and users.

### Large Files
For very large DuckDB files, the conversion may take time. Monitor Snowflake warehouse usage.

### Parquet Upload
The script creates Parquet files and table structures. You may need to manually upload Parquet files to Snowflake stages for data loading, or implement automatic upload functionality.

## Integration with ADE-Bench

The generated Snowflake databases can be used in the ADE-Bench harness by:

1. Updating task configurations to reference Snowflake instead of DuckDB
2. Configuring Snowflake connection parameters in task environments
3. Using the created databases and users for task execution
4. Updating dbt profiles to connect to Snowflake

## Security Notes

- Database passwords are set to simple values for demo purposes
- In production, use strong, unique passwords
- Consider using key-pair authentication instead of passwords
- Review and adjust user privileges as needed for your security requirements
