with matches as (
  select count(*) as column_count 
  from "information_schema"."columns"
  where table_catalog not in ('temp','localmemdb','_duckdb_ui')
)

select * 
from matches 
where column_count != 545