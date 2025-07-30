#!/bin/bash

# Remove the models that need to be created.
rm models/analytics_obt/obt_product_inventory.sql
rm models/warehouse/dim_products.sql
rm models/warehouse/fact_inventory.sql

# Remove the obt_sales_overview model, which depends on removed models.
rm models/analytics_obt/obt_sales_overview.sql

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

dbt deps
dbt run