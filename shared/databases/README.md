# Shared Databases

This directory contains shared database files that can be used across multiple ADE-Bench tasks. Databases are organized by type.

## Directory Structure

- `duckdb/` - DuckDB database files (.duckdb)
- `sqlite/` - SQLite database files (.db, .sqlite)
- `postgres/` - PostgreSQL initialization scripts (.sql)

## Usage

Tasks can reference shared databases in their `task.yaml`:

```yaml
database:
  source: shared
  name: shopify  # Database filename (without extension)
  type: duckdb   # Database type
```

**Important**: Shared databases are always copied into task containers to ensure data integrity. The original database files in this directory are never modified by running tasks.

## Adding New Databases

1. Place the database file in the appropriate type directory
2. Update `catalog.yaml` with database metadata
3. Database will be automatically available to tasks

## Database Naming

- Use descriptive names (e.g., `shopify_sales.duckdb`, `customer_analytics.db`)
- Avoid spaces in filenames
- Include version suffix if needed (e.g., `sales_v2.duckdb`)