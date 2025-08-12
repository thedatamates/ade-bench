with checksum as (
  select 
    count(*) as columns,
    count(case when lower(data_type) = 'timestamp' then 1 else null end) as timestamp_columns
  from information_schema.columns 
  where table_name = 'task_data'
  and column_name in ('due_on','due_at')
)

select * 
from checksum
where columns != 2 or timestamp_columns != 2