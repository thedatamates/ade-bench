#!/bin/bash

# Update the "products" source table to change the id field to a string, and add several new rows that have ids as hashes.
cat > update_products.sql << 'EOF'
-- Update the id field to be a string.
create or replace table main.products_temp as
  select 
    * replace (id::varchar as id)
  from main.products;

-- Add several new rows that have ids as hashes.
insert into main.products_temp 
  select 
    * replace (md5(id) as id)
  from main.products_temp
  where id::int >= 60 and id::int <= 80;

-- Rename the table to the original name.
drop table main.products;
alter table main.products_temp rename to products;
EOF

# Execute the SQL file using Python and DuckDB
python3 -c "
import duckdb
conn = duckdb.connect('analytics_engineering.duckdb')
with open('update_products.sql', 'r') as f:
    sql = f.read()
conn.execute(sql)
conn.close()
print('Duplicates created successfully')
"
# Clean up the SQL file
rm update_products.sql

dbt deps
dbt run