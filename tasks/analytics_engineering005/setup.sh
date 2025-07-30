#!/bin/bash

# Create a SQL file to create duplicates in the inventory table. 
cat > create_duplicates.sql << 'EOF'
insert into main.inventory_transactions
    select * 
    from main.inventory_transactions 
    where mod(product_id,2) = 0;
EOF

# Execute the SQL file using Python and DuckDB
python3 -c "
import duckdb
conn = duckdb.connect('analytics_engineering.duckdb')
with open('create_duplicates.sql', 'r') as f:
    sql = f.read()
conn.execute(sql)
conn.close()
print('Duplicates created successfully')
"
# Clean up the SQL file
rm create_duplicates.sql

# Remove the dedupe function from the fact_inventory model
cat > models/warehouse/fact_inventory.sql << 'EOF'
{{ config(
    partition_by={
        "field": "transaction_created_date",
        "data_type": "date"
    }
) }}

WITH source AS (
    SELECT
        id AS inventory_id,
        transaction_type,
        CAST(STRPTIME(transaction_created_date, '%m/%d/%Y %H:%M:%S') AS DATE) AS transaction_created_date,
        transaction_modified_date,
        product_id,
        quantity,
        purchase_order_id,
        customer_order_id,
        comments,
        get_current_timestamp() AS insertion_timestamp
    FROM {{ ref('stg_inventory_transactions') }}
)

SELECT *
FROM source
EOF

dbt deps
dbt run