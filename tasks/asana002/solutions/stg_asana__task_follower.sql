
with base as (

    select * 
    from {{ source('asana', 'task_follower') }}

),

final as (
    
    select 
        task_id,
        user_id
    from base
)

select * 
from final
