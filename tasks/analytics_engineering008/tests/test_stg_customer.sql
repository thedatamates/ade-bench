with src as (
  select column_name 
  from "information_schema"."columns" 
  where table_name = 'customer'
)

, model as (
  select column_name 
  from "information_schema"."columns" 
  where table_name = 'stg_customer'
)

, combined as (
  select 
    count(m.column_name) as model_names,
    count(s.column_name) as src_names,
    count(case when m.column_name = 'ingestion_timestamp' then 1 else null end) as ingestion_column
  from model m
  left join src s
  on s.column_name = m.column_name
)

select * 
from combined
where model_names != 19
or src_names != 18
or ingestion_column != 1