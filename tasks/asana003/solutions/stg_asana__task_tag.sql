{{ config(enabled=var('asana__using_task_tags', True)) }}

with base as (

    select * 
    from {{ source('asana', 'task_tag') }}

),

final as (
    
    select 
        tag_id,
        task_id
    from base
)

select * 
from final