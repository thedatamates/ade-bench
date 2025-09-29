-- db: snowflake
{% set current_database = target.database %}

with matches as (
  select count(*) as column_count
  from {{current_database}}.information_schema.columns
  where table_schema not in ('INFORMATION_SCHEMA')
)

select *
from matches
where column_count != 519