#!/bin/bash
# Create the product_performance model
cat > models/foo.sql << 'EOF'
select 1 as bar
EOF

# Run dbt to create the models
dbt run --select foo
