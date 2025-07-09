#!/bin/bash
# Create the project and profile files
cat > dbt_project.yml << 'EOF'
name: 'analytics_engineering'
version: '1.0.0'

# This setting configures which "profile" dbt uses for this project.
profile: 'analytics_engineering'

model-paths: ["models"]

models:
  +materialized: table
EOF

cat > profiles.yml << 'EOF'
analytics_engineering:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "./analytics_engineering.duckdb"
      schema: main
EOF

# Create the model directory
mkdir -p models

# Add models to the directory
cat > models/source.yml << 'EOF'
version: 1
sources:
  - name: analytics_engineering
    schema: main
    tables:
      - name: customer
EOF

cat > models/stg_customer.sql << 'EOF'
WITH source AS (
    SELECT * 
    FROM {{ source('analytics_engineering', 'customer') }}
)
SELECT
    *,
    get_current_timestamp() AS ingestion_timestamp
FROM source
EOF



# Run dbt to create the models
dbt run --select stg_customer
