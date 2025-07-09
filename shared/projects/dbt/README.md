# Shared dbt Projects

This directory contains shared dbt project files that can be used across multiple ADE-Bench tasks. dbt projects are organized by name.

## Directory Structure

```
shared/projects/dbt/
├── analytics_engineering/     # dbt project for analytics engineering tasks
├── shopify_analytics/         # dbt project for shopify analytics tasks
├── workday/                   # dbt project for workday tasks
└── activity/                  # dbt project for activity tasks
```

## Usage

Tasks can reference shared dbt projects in their `task.yaml`:

```yaml
project:
  source: shared
  name: analytics_engineering  # project name (directory name)
  type: dbt                   # project type
```

For local projects (default behavior):
```yaml
project:
  source: local  # Or omit project config entirely
  type: dbt
```

## Adding New Projects

1. Place the project directory in `shared/projects/dbt/`
2. Project will be automatically available to tasks

## Project Naming

- Use descriptive names (e.g., `shopify_analytics`, `customer_analytics`)
- Avoid spaces in directory names
- Include version suffix if needed (e.g., `analytics_v2`)

## Important Notes

- Shared projects are always copied into task containers to ensure isolation
- The original project files in this directory are never modified by running tasks
- Each project should be self-contained with its own `dbt_project.yml`, `profiles.yml`, and model files

## Project Types

This directory contains dbt projects. For other project types, see the parent `shared/projects/` directory structure. 