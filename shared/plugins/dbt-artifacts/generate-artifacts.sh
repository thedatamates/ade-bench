#!/bin/bash
set -e

echo "Generating baseline dbt artifacts in target-base directory..."

# Check if dbt project exists
if [ ! -f "/app/dbt_project.yml" ]; then
    echo "Warning: No dbt_project.yml found at /app/dbt_project.yml"
    echo "Skipping artifact generation"
    exit 0
fi

# Navigate to app directory
cd /app

# Create target-base directory if it doesn't exist
mkdir -p target-base

# Install dbt dependencies if needed
if [ -f "packages.yml" ] || [ -f "dependencies.yml" ]; then
    echo "Installing dbt dependencies..."
    dbt deps
fi

# Generate manifest.json via compile
echo "Running dbt compile to generate manifest.json..."
dbt compile --target-path target-base

# Generate catalog.json via docs generate
echo "Running dbt docs generate to generate catalog.json..."
dbt docs generate --target-path target-base

# Verify artifacts were created
if [ -f "target-base/manifest.json" ]; then
    echo "✓ manifest.json generated successfully"
else
    echo "✗ Warning: manifest.json not found in target-base/"
fi

if [ -f "target-base/catalog.json" ]; then
    echo "✓ catalog.json generated successfully"
else
    echo "✗ Warning: catalog.json not found in target-base/"
fi

echo "Baseline dbt artifacts generation complete"
