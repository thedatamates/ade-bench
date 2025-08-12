#!/bin/bash

## Fix the error by changing the data type of the underlying table. 
cat > update_task_data_type.sql << 'EOF'
-- Update the id field to be a string.
create or replace table main.task_data_temp as
  select 
    * replace (due_at::timestamp as due_at)
  from main.task_data;

-- Rename the table to the original name.
drop table main.task_data;
alter table main.task_data_temp rename to task_data;
EOF

# Execute the SQL file using Python and DuckDB
python3 -c "
import duckdb
conn = duckdb.connect('asana.duckdb')
with open('update_task_data_type.sql', 'r') as f:
    sql = f.read()
conn.execute(sql)
conn.close()
"
# Clean up the SQL file
rm update_task_data_type.sql

dbt deps
dbt run
