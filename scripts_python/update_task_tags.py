#!/usr/bin/env python3
"""Update task.yaml files with new tags while preserving formatting."""

import re
from pathlib import Path

# Tag mappings from the provided list
TASK_TAGS = {
    "airbnb001": ["data-inspection", "dbt", "dbt-macros", "dbt-packages", "dbt-utils", "debugging", "jinja", "model-refactor"],
    "airbnb002": ["data-inspection", "dbt", "dbt-macros", "dbt-packages", "dbt-utils", "debugging", "jinja", "model-refactor"],
    "airbnb003": ["dbt", "dbt-macros", "jinja", "model-refactor", "dbt-materialization"],
    "airbnb004": ["data-inspection", "dbt", "model-refactor"],
    "airbnb005": ["dbt", "external-knowledge", "model-creation"],
    "airbnb006": ["dbt", "dbt-hygiene", "model-refactor"],
    "airbnb007": ["dbt", "model-creation", "dbt-materialization", "dbt-project-configuration"],
    "airbnb008": ["dbt", "debugging", "dbt-project-configuration"],
    "airbnb009": ["analysis", "data-inspection", "dbt", "debugging", "model-refactor"],
    "analytics_engineering001": ["dbt", "diagnostic"],
    "analytics_engineering002": ["dbt", "debugging", "model-refactor"],
    "analytics_engineering003": ["dbt", "model-creation"],
    "analytics_engineering004": ["dbt", "model-creation"],
    "analytics_engineering005": ["data-hygiene", "data-inspection", "dbt", "debugging", "model-creation"],
    "analytics_engineering006": ["dbt", "model-creation"],
    "analytics_engineering007": ["data-change", "data-inspection", "dbt", "debugging", "model-refactor"],
    "analytics_engineering008": ["dbt", "model-creation", "dbt-project-configuration"],
    "asana001": ["data-hygiene", "data-inspection", "dbt", "dbt-macros", "debugging", "model-refactor"],
    "asana002": ["dbt", "dbt-hygiene", "dbt-packages", "model-refactor"],
    "asana003": ["data-hygiene", "data-inspection", "dbt", "dbt-packages", "debugging", "model-refactor"],
    "asana004": ["dbt", "model-refactor"],
    "asana005": ["data-change", "data-inspection", "dbt", "debugging", "model-refactor"],
    "f1001": ["dbt", "dbt-hygiene", "debugging", "model-creation", "model-refactor", "dbt-materialization"],
    "f1002": ["dbt", "model-creation"],
    "f1003": ["dbt", "model-creation"],
    "f1004": ["analysis", "data-hygiene", "data-inspection", "dbt", "debugging"],
    "f1005": ["analysis", "data-hygiene", "data-inspection", "dbt", "debugging", "dbt-project-configuration"],
    "f1006": ["analysis", "data-hygiene", "data-inspection", "dbt", "debugging", "dbt-project-configuration"],
    "f1007": ["data-inspection", "dbt", "debugging", "model-refactor"],
    "f1008": ["dbt", "model-creation"],
    "f1009": ["analysis", "dbt", "external-knowledge"],
    "f1010": ["analysis", "dbt", "external-knowledge"],
    "f1011": ["analysis", "dbt", "external-knowledge"],
    "intercom001": ["dbt", "model-creation"],
    "intercom002": ["dbt", "model-creation"],
    "intercom003": ["dbt", "model-creation"],
    "quickbooks001": ["data-hygiene", "dbt", "dbt-packages", "dbt-utils", "debugging", "model-refactor"],
    "quickbooks002": ["dbt", "dbt-hygiene", "dbt-packages", "dbt-utils", "jinja", "model-refactor", "dbt-project-configuration"],
    "quickbooks004": ["dbt", "dbt-hygiene", "dbt-packages", "jinja", "model-refactor", "dbt-project-configuration"],
    "shopify-analytics": [],
    "workday001": [],
}


def update_task_yaml(task_dir: Path):
    """Update the tags in a task.yaml file while preserving formatting."""
    task_yaml = task_dir / "task.yaml"

    if not task_yaml.exists():
        print(f"⚠️  {task_dir.name}: task.yaml not found")
        return

    # Get the new tags for this task
    task_name = task_dir.name
    new_tags = TASK_TAGS.get(task_name)

    if new_tags is None:
        print(f"⚠️  {task_name}: No tags defined in mapping")
        return

    # Read the file content
    content = task_yaml.read_text()

    # Pattern to match the tags section (tags: followed by list items with indentation)
    # This matches from "tags:" through all the "  - tag" lines (with 2-space indent)
    pattern = r'tags:\n(?:  - .*\n)*'

    # Build the new tags section
    if new_tags:
        new_tags_section = "tags:\n" + "\n".join(f"  - {tag}" for tag in new_tags) + "\n"
    else:
        new_tags_section = "tags: []\n"

    # Replace the tags section
    new_content = re.sub(pattern, new_tags_section, content)

    # Only write if content changed
    if new_content != content:
        task_yaml.write_text(new_content)
        print(f"✓ {task_name}: Updated tags to {len(new_tags)} items")
    else:
        print(f"→ {task_name}: No changes needed")


def main():
    """Update all task.yaml files."""
    tasks_dir = Path("tasks")

    if not tasks_dir.exists():
        print("Error: tasks directory not found")
        return

    # Process all task directories
    task_dirs = sorted([d for d in tasks_dir.iterdir() if d.is_dir()])

    print(f"Updating {len(task_dirs)} task.yaml files...\n")

    for task_dir in task_dirs:
        update_task_yaml(task_dir)

    print("\n✅ Done!")


if __name__ == "__main__":
    main()
