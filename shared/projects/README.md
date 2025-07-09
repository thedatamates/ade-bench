# Shared Projects

This directory contains shared project files that can be used across multiple ADE-Bench tasks. Projects are organized by type.

## Directory Structure

```
shared/projects/
├── dbt/                       # dbt projects
│   ├── analytics_engineering/
│   ├── shopify_analytics/
│   ├── workday/
│   └── activity/
├── other/                     # Future project types
└── README.md                  # This file
```

## Project Types

- **dbt**: dbt projects for data transformation tasks
- **other**: Future project types (e.g., Python scripts, SQL files, etc.)

## Usage

Tasks can reference shared projects in their `task.yaml`:

```yaml
project:
  source: shared
  name: analytics_engineering
  type: dbt
```

The `type` field determines which subdirectory the project is loaded from.

## Adding New Project Types

1. Create a new subdirectory in `shared/projects/` for the project type
2. Add the project type to the validation pattern in `ProjectConfig`
3. Update the harness logic if needed for the new project type

## Benefits

- **Organized**: Projects are grouped by type
- **Extensible**: Easy to add new project types
- **Consistent**: Follows the same pattern as shared databases 