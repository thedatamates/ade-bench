
with base as (

    select * 
    from {{ source('asana', 'story') }}

),

final as (
    
    select 
        id as story_id,
        cast(created_at as {{ dbt.type_timestamp() }}) as created_at,
        created_by_id as created_by_user_id,
        target_id as target_task_id,
        text as story_content,
        type as event_type
    from base
)

select * 
from final
