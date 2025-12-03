{{ config(enabled=var('asana__using_task_tags', True)) }}

select * 
from {{ var('task_tag') }}