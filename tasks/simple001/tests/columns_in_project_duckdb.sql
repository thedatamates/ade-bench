-- db: duckdb
with matches as (
  select
    count(case when table_name = 'dimension_customer' then 1 else null end) as dimension_customer_count,
    count(case when table_name = 'stg_customer' then 1 else null end) as stg_customer_count
  from information_schema.tables
  where table_catalog not in ('temp','localmemdb','_duckdb_ui')
    and table_name in ('dimension_customer','stg_customer')
)

select *
from matches
where dimension_customer_count != 1
or stg_customer_count != 1